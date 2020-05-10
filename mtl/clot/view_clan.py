from flask import redirect, render_template, request, session, Blueprint
import sqlite3

from mtl.clot.leaderboard import Leaderboard
from mtl.clot.lot import LOTContainer
from mtl.clot.view_player import templateFrequencyDistribution

from mtl.ladder.config import clot_config
from mtl.ladder.utilities.clan_stat_queries import find_clan_metrics
from mtl.ladder.utilities.dal import find_clan, find_all_finished_games_by_clan, find_player


view_clan_page = Blueprint('view_clan_page', __name__, template_folder='templates', static_folder="/static")


@view_clan_page.route('/clan')
def show():
    try:
        clan_id = int(request.args.get('clanId'))
    except TypeError:
        return redirect("/")
    conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
    clan = find_clan(conn, clan_id)
    clan_metrics = find_clan_metrics(clan)

    leaderboard = Leaderboard(clan)
    container = LOTContainer()

    finished_games = find_all_finished_games_by_clan(conn, clan.name)
    template_stats_win = templateFrequencyDistribution(list([x[0] for x in
                                                             filter(lambda x: x[1] == clan.name, finished_games)]))
    template_stats_lost = templateFrequencyDistribution(list([x[0] for x in
                                                              filter(lambda x: x[1] != clan.name, finished_games)]))

    current_player = None
    if 'authenticatedtoken' in session:
        invite_token = session['authenticatedtoken']
        current_player = find_player(conn, invite_token)

    templates = clot_config.TEMPLATE_NAMES
    template_winrates = []
    for key, value in templates.items():
        total_games = (template_stats_win.get(str(key), 0) + template_stats_lost.get(str(key), 0))
        won_games = template_stats_win.get(str(key), 0)
        winrate = won_games / max(1, total_games)
        if total_games >= 2:
            template_winrates.append({"name": value, "winrate": winrate, "totalGames": total_games, "id": key})

    return render_template('view-clan.html', clan=clan, clan_metrics=clan_metrics, leaderboard=leaderboard,
                           container=container, template_winrates=template_winrates, currentPlayer=current_player)
