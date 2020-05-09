from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound, filters
from lot import LOTContainer
from utilities.DAL import find_clan, find_all_finished_games_by_clan, find_player
from utilities.ClanStatQueries import find_clan_metrics
import sqlite3
from config.ClotConfig import ClotConfig
from leaderboard import Leaderboard
from viewplayer import templateFrequencyDistribution

from datetime import datetime


view_clan_page = Blueprint('view_clan_page', __name__,
                        template_folder='templates', static_folder="/static")

@view_clan_page.route('/clan')
def show():
    try:
        clan_id = int(request.args.get('clanId'))
    except:
        redirect("/")
    conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
    clan = find_clan(conn, clan_id)
    clan_metrics = find_clan_metrics(clan)

    leaderboard = Leaderboard(clan)
    container = LOTContainer()

    finished_games = find_all_finished_games_by_clan(conn, clan.name)
    template_stats_win = templateFrequencyDistribution(list([x[0] for x in filter(lambda x: x[1] == clan.name , finished_games)]))
    template_stats_lost = templateFrequencyDistribution(list([x[0] for x in filter(lambda x: x[1]!= clan.name , finished_games)]))

    currentPlayer = None
    if 'authenticatedtoken' in session:
        inviteToken = session['authenticatedtoken']
        currentPlayer = find_player(conn, (inviteToken))

    templates = ClotConfig.template_names
    template_winrates = []
    for key, value in templates.items():
        total_games = (template_stats_win.get(str(key), 0) + template_stats_lost.get(str(key), 0))
        won_games = template_stats_win.get(str(key), 0)
        winrate = won_games / max(1, total_games);
        if total_games >= 2 :
            template_winrates.append({"name": value, "winrate": winrate, "totalGames": total_games, "id": key})


    return render_template('viewclan.html', clan = clan, clan_metrics = clan_metrics, leaderboard = leaderboard, container = container, template_winrates = template_winrates, currentPlayer = currentPlayer)

