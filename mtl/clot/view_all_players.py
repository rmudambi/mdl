from flask import render_template, Blueprint

from mtl.clot.lot import LOTContainer


view_all_players_page = Blueprint('view_all_players_page', __name__, template_folder='templates',
                                  static_folder="/static")


@view_all_players_page.route('/allplayers')
def show():
    container = LOTContainer()
    return render_template('view-all-players.html', container = container)
