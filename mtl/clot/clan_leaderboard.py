from flask import render_template, Blueprint

from mtl.ladder.utilities.clan_stat_queries import (find_clan_leaderboard, ACTIVE_PLAYERS, TOTAL_GAMES, WIN_RATE, WINS,
                                                    ALL_TIME_HIGHEST_RATING, ALL_TIME_HIGHEST_RANK,
                                                    CURRENT_AVERAGE_RATING, CURRENT_HIGHEST_RATING,
                                                    PLAYERS_WITH_FIRST_RANK, PLAYERS_WITH_TOP_5, PLAYERS_WITH_TOP_10, )
from mtl.clot.lot import LOTContainer


clan_leaderboard_page = Blueprint('clan_leaderboard_page', __name__, template_folder='templates',
                                  static_folder="/static")


@clan_leaderboard_page.route('/clan-leaderboard')
def show():
    container = LOTContainer()
    clan_leaderboard = ClanLeaderboard()
    return render_template('clan-leaderboard.html', container=container, clan_leaderboard=clan_leaderboard)


class ClanLeaderboard:
    def __init__(self):
        self.active_players = find_clan_leaderboard(ACTIVE_PLAYERS)
        self.games_played = find_clan_leaderboard(TOTAL_GAMES)
        self.wins = find_clan_leaderboard(WINS)

        self.all_time_highest_rating = find_clan_leaderboard(ALL_TIME_HIGHEST_RATING)
        self.all_time_highest_rank = find_clan_leaderboard(ALL_TIME_HIGHEST_RANK, False)
        self.current_highest_rating = find_clan_leaderboard(CURRENT_HIGHEST_RATING)

        self.top1 = find_clan_leaderboard(PLAYERS_WITH_FIRST_RANK)
        self.top5 = find_clan_leaderboard(PLAYERS_WITH_TOP_5)
        self.top10 = find_clan_leaderboard(PLAYERS_WITH_TOP_10)

        self.win_rate = []
        self.current_average_rating = []
        win_rate_all_clans = find_clan_leaderboard(WIN_RATE)
        current_average_rating_all_clans = find_clan_leaderboard(CURRENT_AVERAGE_RATING)

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
