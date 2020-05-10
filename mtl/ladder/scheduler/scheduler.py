from datetime import datetime
from itertools import islice
import random
import requests

from bs4 import BeautifulSoup
import sqlite3

from mtl.ladder.config import clot_config
# TODO replace
from mtl.ladder.config.Backup import backup_database
from mtl.ladder.config.game_message import GameMessage
from mtl.ladder.entities.game import Game
from mtl.ladder.scheduler import game_util
from mtl.ladder.utilities import elo
from mtl.ladder.utilities.api import createGame, queryGame, validate_token, APIError
from mtl.ladder.utilities.clan_league_logging import get_logger
from mtl.ladder.utilities.clan_stat_queries import compute_clan_stats
from mtl.ladder.utilities.dal import (DataError, find_all_pending_games, find_all_players, find_all_recent_games,
                                      find_all_unexpired_games, find_games_since_last_update, find_history_records,
                                      find_joined_players, find_last_n_games, find_players_on_vacation, find_vetoes,
                                      insert_game, insert_history_record, insert_or_update_clan, update_games,
                                      update_player, update_players)
from mtl.ladder.utilities.stat_queries import update_leaderboards, update_mdl_stats

logger = get_logger()


class Scheduler:
    @staticmethod
    def create_player_pairs(players_sorted_by_rating, players_to_be_allocated_new_games, recent_games):
        # Remove players who have not reached their max game count.
        eligigble_players_sorted_by_rating = [player for player in players_sorted_by_rating
                                              if player.player_id in players_to_be_allocated_new_games]

        # Dict containing each player as key, and list of players they have played as value
        # {p1:[p2,p3]}
        recent_matchups = {}
        for game in recent_games:
            recent_matchups.setdefault(game.team_a, set()).add(game.team_b)
            recent_matchups.setdefault(game.team_b, set()).add(game.team_a)

        # Pairs of players to be returned
        player_pairs = []
        num_of_players = len(eligigble_players_sorted_by_rating)
        for i in range(1, num_of_players + 1):
            first_player = eligigble_players_sorted_by_rating[i - 1]

            # find possible opponents with a similar rating(20 above/below)
            start = max(0, i - 20)
            possible_opponents = list(islice(eligigble_players_sorted_by_rating, start, i + 20))
        
            # player cannot play himself
            possible_opponents.remove(first_player)
        
            eligible_opponents = list(possible_opponents)
            for opponent in possible_opponents:
                # opponent has already been allotted max number of games.
                if players_to_be_allocated_new_games[opponent.player_id] == 0:
                    eligible_opponents.remove(opponent)
                    continue
        
                # They have already played recently    
                if (recent_matchups is not None and first_player.player_id in recent_matchups.keys()
                        and opponent.player_id in recent_matchups[first_player.player_id]):
                    eligible_opponents.remove(opponent)
                    continue
        
            # Find opponents till no more games are to be allocated for this player
            while players_to_be_allocated_new_games[first_player.player_id] != 0:
                if len(eligible_opponents) == 0:
                    # No suitable opponent found
                    break    
            
                # randomly pick the opponent 
                second_player = random.choice(eligible_opponents)
            
                players_to_be_allocated_new_games[first_player.player_id] -= 1
                players_to_be_allocated_new_games[second_player.player_id] -= 1
            
                player_pairs.append([first_player, second_player])
            
                # remove second_player as possible opponent for further game allocation
                eligible_opponents.remove(second_player)            
            
                # also add this to recent matchups
                recent_matchups.setdefault(first_player.player_id, set()).add(second_player.player_id)
                recent_matchups.setdefault(second_player.player_id, set()).add(first_player.player_id)
            
        return player_pairs

    @staticmethod
    def schedule_games():
        logger.info("Scheduling games")
        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM

        # Find all recent games in the last 5 days. Active games also count as recent.
        # All players who have played each other recently, will not be paired together. 
        recent_games = find_all_recent_games(conn)
        joined_players = find_joined_players(conn)
        
        # Map of {playerId:NumOfGamesToBeAllotted}
        players_to_be_allocated_new_games = {}

        active_games = find_all_pending_games(conn)
        # List of all playerIds who have games. 
        # If a player has N games, that playerId will be present N times.
        player_ids_in_active_games = [int(team) for game in active_games for team in (game.team_a, game.team_b)]

        # Initially assign max games as games to be allotted.
        for player in joined_players:
            players_to_be_allocated_new_games[player.player_id] = player.max_games

            # Check if players have recently changed their game count. If their wait_cycles > 0, do not allocate games
            # to them in this CLOT cycle.
            if player.wait_cycles is not None and player.wait_cycles > 0:
                # Decrement the wait_cycles
                player.wait_cycles -= 1
                update_player(conn, player)

                # Set this player's game allocation count to 0 for this CLOT cycle.
                players_to_be_allocated_new_games[player.player_id] = 0

        # Subtract active games for the player from their max game count.
        # Ensure > 0. (Can go -ve when players reduce their game count)
        for pId in player_ids_in_active_games:
            if pId in players_to_be_allocated_new_games.keys():
                if players_to_be_allocated_new_games[pId] > 0:
                    players_to_be_allocated_new_games[pId] -= 1

        players_sorted_by_rating = sorted(joined_players, key=lambda p: p.Rating, reverse=True)

        # Create matchups.
        player_pairs = Scheduler.create_player_pairs(players_sorted_by_rating, players_to_be_allocated_new_games,
                                                     recent_games)
        for pair in player_pairs:
            # Init templates to ensure previous pair's vetoes don't eliminate the templates for this pair too.
            templates = list(clot_config.TEMPLATE_NAMES.keys())
            player_a_vetoed_templates = find_vetoes(conn, pair[0].player_id, clot_config.TEMPLATE_VETO_MAX)
            player_b_vetoed_templates = find_vetoes(conn, pair[1].player_id, clot_config.TEMPLATE_VETO_MAX)

            # Exclude all templates from the template pool which have been vetoed by either player.
            for created_date, template_id in player_a_vetoed_templates:
                if template_id in templates:
                    templates.remove(template_id)
            for created_date, template_id in player_b_vetoed_templates:
                if template_id in templates:
                    templates.remove(template_id)

            player_a_last_n_games = find_last_n_games(conn, pair[0].player_id, clot_config.RECENT_GAMES)
            player_b_last_n_games = find_last_n_games(conn, pair[1].player_id, clot_config.RECENT_GAMES)
            
            # Exclude all templates from the template pool which have been used in the last N games for either player.
            for game in player_a_last_n_games:
                template_id = int(game.template)
                if template_id in templates:
                    templates.remove(template_id)
            for game in player_b_last_n_games:
                template_id = int(game.template)
                if template_id in templates:
                    templates.remove(template_id)

            # From a list of filtered_templates, a random one is picked for each game
            template_id = int(random.choice(templates))

            game_name = game_util.get_game_name(pair[0].player_name, pair[1].player_name)
            teams = [(i, p.player_id) for i, p in enumerate(pair)]

            # If the template bonuses are to be randomized, get the example game Id
            example_game = None
            overridden_bonuses = False
            if template_id in clot_config.RANDOMIZED_TEMPLATES:
                overridden_bonuses = True
                example_game = clot_config.RANDOMIZED_TEMPLATES[template_id]

            if template_id in GameMessage.messages:
                message = "{0} \n\n{1}".format(game_util.DEFAULT_GAME_MESSAGE, GameMessage.messages[template_id])
            else:
                message = game_util.DEFAULT_GAME_MESSAGE

            game_id = createGame(clot_config.EMAIL, clot_config.TOKEN, template=template_id,
                                 gameName=game_name, message=message, teams=teams,
                                 overriddenBonuses=overridden_bonuses, exampleGame=example_game)
            game = Game(CreatedDate=datetime.now(), GameId=game_id, TeamA=pair[0].player_id, TeamB=pair[1].player_id,
                        Template=template_id)

            # Add game to the db
            conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
            insert_game(conn, game)

    @staticmethod
    def check_game_status():
        logger.info("Checking game status")
        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
        all_pending_games = find_all_pending_games(conn)
        for game in all_pending_games:            
            response = queryGame(clot_config.EMAIL, clot_config.TOKEN, game.game_id)
            teams = [game.team_a, game.team_b]

            is_any_player_on_vacation = False
            for team in teams:
                try:
                    # Check if player is on vacation
                    vac_resp = validate_token(clot_config.EMAIL, clot_config.TOKEN, team)
                    if 'onVacationUntil' in vac_resp:
                        is_any_player_on_vacation = True
                        break
                except APIError:
                    # Validate API failed. Player has probably blacklisted MotD[2] and we don't care if they are on
                    # vacation.
                    pass

            # Parse response and update winning team.
            game_util.update_game_winner(response, teams, is_any_player_on_vacation)

    @staticmethod
    def update_ratings(current_date=None):
        logger.info("Updating ratings")
        if current_date is None:
            current_date = datetime.now()

        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
        recently_finished_games = find_games_since_last_update(conn, current_date)
        players = {}
        for player in find_all_players(conn):
            players[player.player_id] = player
        for game in recently_finished_games:
            player_a = players.get(game.team_a)
            player_b = players.get(game.team_b)

            # Compute Elo rating changes
            result = (1 if game.winner == game.team_a else 0)
            player_a.Rating, player_b.Rating = elo.get_updated_rating(player_a.Rating, player_b.Rating, result)

            # Update activity bonus(capped at a max of 80)
            player_a.increment_activity_bonus()
            player_b.increment_activity_bonus()

            # Update displayed rating
            player_a.update_displayed_rating()
            player_b.update_displayed_rating()

            # Mark IsRatingUpdated as true on all these games
            game.is_rating_updated = True

        if len(recently_finished_games) > 0:
            update_players(conn, players.values())
            update_games(conn, recently_finished_games)

    @staticmethod
    def update_players_on_vacation() -> None:
        logger.info("Returning players from vacation")
        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)
        players = find_players_on_vacation(conn)
        players_returning = []
        for player in players:
            response = validate_token(clot_config.EMAIL, clot_config.TOKEN, player.player_id)
            if 'onVacationUntil' not in response:
                player.return_from_vacation()
                players_returning.append(player)
        
        if players_returning:
            update_players(conn, players_returning)

    @staticmethod
    def update_players_rank_status(current_date: datetime = None) -> None:
        logger.info("Updating ranks")
        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
        players = find_all_players(conn)
        
        for player in players:
            # Check if player has over 20 unexpired games. If not, player cannot be ranked.
            unexpired_games = find_all_unexpired_games(conn, player.player_id, current_date)
            if len(unexpired_games) >= 20 and player.is_joined:
                player.is_ranked = True
            else:
                player.unrank_player()

            # Check if player is on vacation
            try:
                response = validate_token(clot_config.EMAIL, clot_config.TOKEN, player.player_id)
                if 'blacklisted' in response:
                    player.update_status_on_leave(False)
                elif 'onVacationUntil' in response:
                    player.update_status_on_leave(True)
                else:
                    # Update name and clan changes for player as well.
                    player.player_name = response['name']
                    if 'clan' in response.keys():
                        player.clan = response['clan']
            except APIError:
                # Validate API failed.
                pass

        # Sort by displayed_rating
        ranked_players = [player for player in players if player.is_ranked]
        sorted_ranked_players = sorted(ranked_players, key=lambda p: p.displayed_rating, reverse=True)
        
        # Update rank, best rank and displayed_rating for each ranked player.
        for i, player in enumerate(sorted_ranked_players):
            player.rank = i + 1
            if player.best_displayed_rating is None or player.best_displayed_rating < player.displayed_rating:
                player.best_displayed_rating = player.displayed_rating
            if player.best_rank is None or player.best_rank > i + 1:
                player.best_rank = i + 1

        update_players(conn, players)

    @staticmethod
    def update_daily_history(conn):
        logger.info("Updating daily history...")
        today = datetime.now().date()
        players = find_all_players(conn)
        ranked_players = {}
        unranked_players = {}
        for player in players:
            if player.is_ranked:
                ranked_players[player.player_id] = player
            else:
                unranked_players[player.player_id] = player

        # Contains ranked players sorted by displayed_rating.
        sorted_ranked_players = sorted(ranked_players.values(), key=lambda p: p.displayed_rating, reverse=True)

        # Create history record for all ranked players
        for rank, player in enumerate(sorted_ranked_players):
            history_record = (today, player.player_id, rank + 1, player.displayed_rating)
            insert_history_record(conn, history_record)

    @staticmethod
    def update_clan_tags(conn):
        logger.info("Updating clan tags...")
        url = 'https://www.warlight.net/Clans/List'
        response = requests.get(url)
        text_soup = BeautifulSoup(response.content, features="html.parser")

        links_container = text_soup.find("div", {"id": "AutoContainer"})
        links = links_container.ul.findAll("a")
        for link in links:
            try:
                clan_id = link.attrs["href"].split('=')[1]
                if len(link.contents) == 2:
                    clan_name = link.contents[1].contents[0].strip()
                else:
                    clan_name = link.contents[-1].strip()
                images = link.findAll("img")
                image = images[0].attrs["src"] if images else None
                if clan_name and clan_id and image:
                    insert_or_update_clan(conn, (clan_id, clan_name, image))
            except Exception as e:
                logger.error(e)

    @staticmethod
    def update_player_clan_affiliation(conn):
        logger.info("Updating player clan affiliation...")
        players = find_all_players(conn)
        for player in players:
            try:
                # Call the warlight API to get the name and clan.
                apiret = validate_token(clot_config.EMAIL, clot_config.TOKEN, player.player_id)
                current_name = apiret['name']
                current_clan = None
                if 'clan' in apiret.keys(): 
                    current_clan = apiret['clan']

                player.player_name = current_name
                player.clan = current_clan
                update_player(conn, player)
            except APIError:
                # Validate API failed. Player has probably blacklisted MotD[2]. Do nothing.
                pass

    @staticmethod
    def daily_rating_decay(conn, current_date=None):
        logger.info("Executing rating decay...")
        players = find_all_players(conn)
                
        for player in players:
            # Decay all players' activity bonus by 2% every day
            player.decay_activity_bonus()
            player.update_displayed_rating()

            # Converge players' rating towards 1500. 
            # If their current rating > 1500, it decreases by 1 every day if they have no unexpired games
            # If their current rating < 1500, it increases by 1 every day if they have no unexpired games
            unexpired_games = find_all_unexpired_games(conn, player.player_id, current_date)
            if len(unexpired_games) == 0:
                player.converge_actual_rating()

            update_player(conn, player)

    @staticmethod
    def run_daily_tasks(current_date=None):
        logger.info("Running daily tasks")
        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)
        today = datetime.now().date()
        history_records = find_history_records(conn, recorded_date=today)

        # If a record exists in the history table for today, the daily tasks have already been completed and there is
        # no work to be done.
        if len(history_records) == 0:
            Scheduler.daily_rating_decay(conn, current_date)
            Scheduler.update_daily_history(conn)
            Scheduler.update_clan_tags(conn)
            Scheduler.update_player_clan_affiliation(conn)

            logger.info("Update MTL stats")
            update_mdl_stats(conn)

    @staticmethod
    def run(current_date: datetime = None) -> None:
        try:
            Scheduler.check_game_status()
            Scheduler.update_ratings(current_date)
            Scheduler.update_players_on_vacation()
            Scheduler.update_players_rank_status(current_date)
            Scheduler.schedule_games()
            Scheduler.run_daily_tasks(current_date)
            update_leaderboards()
            compute_clan_stats()

            # logger.info("Backing up database")
            # backup_database()

            logger.info("Last run time - %s", datetime.now().strftime('%m/%d/%Y - %H:%M:%S'))
        except Exception as ex:
            logger.error("Failed with - %s", ex)
