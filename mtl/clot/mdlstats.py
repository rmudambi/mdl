from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound, filters
from lot import LOTContainer
from utilities.StatQueries import *
from datetime import datetime
from config.ClotConfig import ClotConfig


mdl_stats_page = Blueprint('mdl_stats_page', __name__,
                        template_folder='templates', static_folder="/static")

@mdl_stats_page.route('/mdlstats')
def show():
    container = LOTContainer()
    mdlStats = MDLStats()

    return render_template('mdlstats.html', container = container, mdlStats = mdlStats)

class MDLStats:
    def __init__(self):
        self.vetoes_per_template = find_vetoes_per_template()
        self.total_games_over_time = find_mdl_stats_by_metric(mdl_stat_finished_games)
        self.games_per_day_over_time = find_mdl_stats_by_metric(mdl_stat_finished_games_per_day)
        self.days_since_launch = (datetime.now() - datetime.strptime("2016-10-25", '%Y-%m-%d')).days
        self.number_of_templates_used = len(ClotConfig.template_names)
        self.number_of_active_players = find_number_of_active_players()
        self.total_number_of_players = find_total_number_of_players()
        self.number_of_ongoing_games = find_number_of_ongoing_games()




