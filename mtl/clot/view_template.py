from flask import redirect, render_template, request, Blueprint
import sqlite3

from mtl.clot.lot import LOTContainer
from mtl.ladder.config import clot_config
from mtl.ladder.utilities.dal import find_template_games


view_template_page = Blueprint('view_template_page', __name__, template_folder='templates', static_folder="/static")


# This page follows the instructions at http://wiki.warlight.net/index.php/CLOT_Authentication
@view_template_page.route('/template')
def show():
    try:
        template_id = int(request.args.get('templateId'))
    except TypeError:
        return redirect("/")
    conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
#    player = find_player(conn, player_id)
    if template_id in clot_config.TEMPLATE_NAMES:
        template_name = clot_config.TEMPLATE_NAMES[template_id]
    else:
        template_name = clot_config.RETIRED_TEMPLATE_NAMES[template_id]
 
    games = find_template_games(conn, template_id)
#    history = find_history_records(conn, player_id=player_id)
    
    finished_games = []
    for game in games:
        if game.finish_date is not None:
            finished_games.append(game)

    finished_games = sorted(finished_games, key=lambda g: g.finish_date, reverse=True)
   
    template_protip = ""
    if template_id in clot_config.TEMPLATE_PROTIPS:
        template_protip = clot_config.TEMPLATE_PROTIPS[template_id]

    container = LOTContainer()
    return render_template('view-template.html', games=finished_games, container=container, template_id=template_id,
                           template_name=template_name, template_protip=template_protip)
