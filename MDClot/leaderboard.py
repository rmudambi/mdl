from flask import Blueprint, render_template

from entities.Clan import Clan
from utilities.StatQueries import find_metric_leaderboard, find_player_leaderboard_by_clan, leaderboard_metadata

from utilities.metricleaderboard import GAME_COUNT, PERCENTAGE, WINS, LEADERBOARD_METRICS as METRICS
from lot import LOTContainer


leaderboard_page = Blueprint('leaderboard_page', __name__, template_folder='templates', static_folder="/static")


leaderboard_metrics = [(metadata.metric_name, metadata.metric_unit) for metadata in leaderboard_metadata]
clan_page_metrics = [
    (METRICS.MOST_GAMES_PLAYED, GAME_COUNT),
    (METRICS.BEST_WIN_RATE, PERCENTAGE),
    (METRICS.LONGEST_WIN_STREAK, WINS)
]


@leaderboard_page.route('/leaderboard')
def show():
    container = LOTContainer()
    leaderboard = Leaderboard()
    return render_template('leaderboard.html', container=container, leaderboard=leaderboard)


class Leaderboard:
    def __init__(self, clan: Clan = None):
        self.metric_leaderboards = [
            LeaderboardTable(metric[0], metric[1], clan) 
            for metric in (clan_page_metrics if clan else leaderboard_metrics)
        ]


class LeaderboardTable:
    def __init__(self, metric_name: str, metric_unit: str, clan: Clan = None):
        self.metric_name = metric_name
        self.metric_unit = metric_unit
        if clan:
            self.player_tuples = find_player_leaderboard_by_clan(clan, metric_name)
        else:
            self.player_tuples = find_metric_leaderboard(metric_name)
        self.clan = clan
