import sqlite3

from mtl.ladder.config import clot_config
from mtl.ladder.utilities.dal import find_all_clans, find_all_games, find_all_players, find_recent_unexpired_games


class LOTContainer:
    def __init__(self):
        
        # (k,v) = (player_id, player)
        self.all_players = {}

        # (k,v) = (clan_name, clan)
        self.all_clans = {}

        self.templates = list(clot_config.TEMPLATE_NAMES.keys())
        self.templates_names = clot_config.TEMPLATE_NAMES

        # (k,v) = (player_id, player)
        self.ranked_players = {}  # Contains players joined on the ladder and have finished 20 games.
        self.joined_players = {}
        active_unranked_players = {}
        inactive_unranked_players = {}

        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
        self.finished_games = find_recent_unexpired_games(conn)
        all_games = find_all_games(conn)
        self.total_game_count = len(all_games)

        clans = find_all_clans(conn)
        for clan in clans:
            self.all_clans[clan.name] = clan

        players = find_all_players(conn)
        for player in players:
            self.all_players[player.player_id] = player
            if player.is_ranked:
                self.ranked_players[player.player_id] = player
                self.joined_players[player.player_id] = player
            else:
                if player.is_joined:
                    active_unranked_players[player.player_id] = player
                    self.joined_players[player.player_id] = player
                else:
                    inactive_unranked_players[player.player_id] = player

        self.joined_players = sorted(self.joined_players.values(), key=lambda p: p.displayed_rating)

        # Contains ranked players sorted by rating. 
        # After the ranked players have been placed at the top, the un-ranked players are sorted below them
        self.players_sorted_by_rating = [] 
        self.sorted_ranked_players = sorted(self.ranked_players.values(), key=lambda p: p.rank)
        sorted_active_unranked_players = sorted(active_unranked_players.values(),
                                                key=lambda p: p.displayed_rating, reverse=True)
        sorted_inactive_unranked_players = sorted(inactive_unranked_players.values(), key=lambda p: p.displayed_rating,
                                                  reverse=True)

        self.players_sorted_by_rating.extend(self.sorted_ranked_players)
        self.players_sorted_by_rating.extend(sorted_active_unranked_players)
        self.players_sorted_by_rating.extend(sorted_inactive_unranked_players)
