from flask import abort, redirect, render_template, session, Blueprint
from jinja2 import TemplateNotFound
import sqlite3

from mtl.clot.lot import LOTContainer
from mtl.ladder.config import clot_config
from mtl.ladder.utilities.dal import find_player, update_player

leave_page = Blueprint('leave_page', __name__, template_folder='templates', static_folder="/static")


@leave_page.route('/leave')
def show():
    try:
        if 'authenticatedtoken' not in session:
            redirect_url = "http://warlight.net/CLOT/Auth?p={0}&state=leave".format(clot_config.PROFILE_ID)
            return redirect(redirect_url)

        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
        player_token = session['authenticatedtoken']

        # Find the player by their token
        player = find_player(conn, player_token)
        if player is None:
            return "Invite token is invalid.  Please contact the CLOT author for assistance."

        player.update_status_on_leave()
        update_player(conn, player)

        # Update container with latest players
        container = LOTContainer()

        return render_template('leave.html', container=container)
    except TemplateNotFound as e:
        print(str(e))
        abort(404)
