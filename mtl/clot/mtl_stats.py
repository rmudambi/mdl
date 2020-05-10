from datetime import datetime

from flask import render_template, Blueprint

from mtl.clot.lot import LOTContainer
from mtl.ladder.config import clot_config
from mtl.ladder.utilities.stat_queries import (find_mdl_stats_by_metric,
                                               find_number_of_active_players,
                                               find_number_of_ongoing_games,
                                               find_total_number_of_players,
                                               find_vetoes_per_template,
                                               mdl_stat_finished_games,
                                               mdl_stat_finished_games_per_day)


mtl_stats_page = Blueprint('mtl_stats_page', __name__, template_folder='templates', static_folder="/static")


@mtl_stats_page.route('/mtl-stats')
def show():
    container = LOTContainer()
    mtl_stats = MTLStats()

    return render_template('mtl-stats.html', container=container, mdlStats=mtl_stats)


class MTLStats:
    def __init__(self):
        self.vetoes_per_template = find_vetoes_per_template()
        self.total_games_over_time = find_mdl_stats_by_metric(mdl_stat_finished_games)
        self.games_per_day_over_time = find_mdl_stats_by_metric(mdl_stat_finished_games_per_day)
        self.days_since_launch = (datetime.now() - datetime.strptime("2016-10-25", '%Y-%m-%d')).days
        self.number_of_templates_used = len(clot_config.TEMPLATE_NAMES)
        self.number_of_active_players = find_number_of_active_players()
        self.total_number_of_players = find_total_number_of_players()
        self.number_of_ongoing_games = find_number_of_ongoing_games()
