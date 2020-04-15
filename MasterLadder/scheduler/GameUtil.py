from enum import Enum
from utilities.DAL import *
from config.ClotConfig import  ClotConfig
from datetime import datetime
from utilities.api import deleteGame
import random
from utilities.clan_league_logging import get_logger
import sqlite3

logger = get_logger()


class GameUtil:
    Message = ("This game has been created by MDL. If you fail to join it within 3 days, vote to end or decline, " 
                "it will count as a loss. For latest standings, please visit http://md-ladder.cloudapp.net/")
    GameSheetName = "All Games"

    class GameState:
        in_progress = "In Progress"
        won = "Won"
        loss = "Loss"
        not_started = ''

    @staticmethod
    def get_game_name(team_a, team_b, template_name):
        team_a = team_a[:18]
        team_b = team_b[:18]
        template_name = template_name[:9]
        name = "{0}|{1} vs {2}".format(ClotConfig.tournament_name, team_a, team_b)
        name = name[:50]

        return name

    @staticmethod
    def update_game_winner(api_response, teams, is_any_player_on_vacation):
        id = api_response.get('id')
        state = api_response.get('state')

        conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
        game = find_game(conn, id)

        winner = None
        if state == 'Finished':
            #It's finished. Record the winner and save it back.
            winner = GameUtil.parse_winner(api_response)
        elif state == 'WaitingForPlayers':
            if not is_any_player_on_vacation:
                # Strip off the tick info.
                created_date = datetime.strptime(game.created_date[:game.created_date.rindex(" ")+9], '%Y-%m-%d %H:%M:%S')
                #It's in the lobby still. Check if it's been too long.
                elapsed = datetime.now() - created_date
                if elapsed.days < ClotConfig.max_days_to_join_game:
                    logger.info("Game %s is in the lobby for %s days.", id, elapsed)
                else:
                    logger.info("Game %s is stuck in the lobby. Marking it as a loss for anyone who didn't join and deleting it.", id)

                    try:
                        ##Delete it over at warlight.net so that players know we no longer consider it a real game
                        deleteGame(ClotConfig.email, ClotConfig.token, id)

                        # Update IsGameDeleted to true.
                        game.is_game_deleted = True

                        winner = GameUtil.parse_winner_of_deleted_game(api_response)
                        logger.info("Game %s was marked deleted", id)
                    except:
                        # If the API doesn't return success, just ignore this game on this run. This can happen if the game 
                        # just started between when we checked its status and when we told it to delete.
                        logger.info("Delete game %s did not return success. Ignoring this game for this run.", id)
            else:
                logger.info("The game is waiting on one of the players who is on vacation")
        else:
            #It's still going.
            logger.info('Game %s is not finished, state = %s, numTurns= %s', id, state, api_response['numberOfTurns'])
        
        if winner is not None:
            # Update game with result
            game.winner = teams[int(winner)]
            conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
            update_game(conn, game)

    @staticmethod
    def parse_winner(api_response):
        """Simple helper function to return the Player who won the game.  This takes json data returned by the GameFeed 
        API.  We just look for a player with the "won" state."""
        winners = [p for p in api_response['players'] if p['state'] == 'Won']
        if len(winners) == 0:
            #The only way there can be no winner is if the players VTE.  Just pick one at random.
            return random.choice(api_response['players'])["team"]
        else:
            return winners[0]["team"]

    @staticmethod
    def parse_winner_of_deleted_game(api_response):
        """Simple helper function to return the Player who should be declared the winner of a game that never began.
        If it didn't begin, it's because someone either didn't join the game or declined it.  They'll be considered
        the loser, so whoever joined is the winner by default."""
        joined = [p for p in api_response['players'] if p['state'] == 'Playing']
        if len(joined) > 0:
            return random.choice(joined)["team"]
    
        """If everyone declined or failed to join, we just pick the winner randomly."""
        return random.choice(api_response['players'])["team"]

   
