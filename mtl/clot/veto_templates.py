from flask import session, redirect, request, Blueprint
import sqlite3

from mtl.ladder.utilities.dal import find_player, insert_veto, delete_vetoes
from mtl.ladder.config import clot_config
from datetime import datetime


veto_templates_page = Blueprint('veto_templates_page', __name__, template_folder='templates', static_folder="/static")


@veto_templates_page.route('/veto')
def show():
    if 'authenticatedtoken' not in session:
        return redirect('/')

    conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
    # Find the player by their token
    player_id = session['authenticatedtoken']
    player = find_player(conn, player_id)
    # Redirect if not the logged in user
    if player.player_id != player_id:
        return redirect('/')

    param_templates = request.args.get('templates')
    if not param_templates:
        # No templates vetoed. Insert a record with template Id as -1 to indicate no templates have been vetoed.
        veto_record = (datetime.now(), player_id, -1)
        # Flush existing vetoes before inserting new ones.
        delete_vetoes(conn, player_id)
        insert_veto(conn, veto_record)
    else:
        new_veteod_templates = [int(template_id) for template_id in param_templates.split(",")]
        if len(new_veteod_templates) > clot_config.TEMPLATE_VETO_MAX:
            raise Exception("Only " + clot_config.TEMPLATE_VETO_MAX + " templates can be vetoed.")

        # Flush existing vetoes before inserting new ones.
        delete_vetoes(conn, player_id)
        veto_time = datetime.now()
        for template_id in new_veteod_templates:
            veto_record = (veto_time, player_id, template_id)
            insert_veto(conn, veto_record)

    redirect_url = "/player?playerId={0}".format(player_id)
    return redirect(redirect_url)
