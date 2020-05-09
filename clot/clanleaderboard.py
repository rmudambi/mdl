from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound
from utilities.ClanStatQueries import *
from lot import LOTContainer
import sqlite3


clan_leaderboard_page = Blueprint('clan_leaderboard_page', __name__,
                        template_folder='templates', static_folder="/static")

@clan_leaderboard_page.route('/clanleaderboard')
def show():
    container = LOTContainer()
    clan_leaderboard = ClanLeaderboard()
    return render_template('clanleaderboard.html', container = container, clan_leaderboard = clan_leaderboard)

class ClanLeaderboard:
    def __init__(self):
        conn = sqlite3.connect(ClotConfig.database_location)
        self.active_players = find_clan_leaderboard(active_players)
        self.games_played = find_clan_leaderboard(total_games)
        self.wins = find_clan_leaderboard(wins)

        self.all_time_highest_rating = find_clan_leaderboard(all_time_highest_rating)
        self.all_time_highest_rank = find_clan_leaderboard(all_time_highest_rank, False)
        self.current_highest_rating = find_clan_leaderboard(current_highest_rating)

        self.top1 = find_clan_leaderboard(players_with_first_rank)
        self.top5 = find_clan_leaderboard(players_with_top5)
        self.top10 = find_clan_leaderboard(players_with_top10)

        self.win_rate = []
        self.current_average_rating = []
        win_rate_all_clans = find_clan_leaderboard(win_rate)
        current_average_rating_all_clans = find_clan_leaderboard(current_average_rating)

        clans_with_three_plus_active_players = []
        for clan_tuple in self.active_players:
            if float(clan_tuple[1]) >= 3:
                clans_with_three_plus_active_players.append(clan_tuple[0])

        # Only consider win rates for clans with 3 or more active players.
        for clan_tuple in win_rate_all_clans:
            if clan_tuple[0] in clans_with_three_plus_active_players:
                self.win_rate.append(clan_tuple)

        # Only consider current_average_rating for clans with 3 or more active players.
        for clan_tuple in current_average_rating_all_clans:
            if clan_tuple[0] in clans_with_three_plus_active_players:
                self.current_average_rating.append(clan_tuple)

