from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound, filters
from mtl.clot.lot import LOTContainer
from mtl.ladder.utilities.DAL import find_player, find_template_games
import sqlite3
from mtl.ladder.config.ClotConfig import ClotConfig
from datetime import datetime


view_template_page = Blueprint('view_template_page', __name__, template_folder='templates', static_folder="/static")

#This page follows the instructions at http://wiki.warlight.net/index.php/CLOT_Authentication
@view_template_page.route('/template')
def show():
    try:
        template_id = int(request.args.get('templateId'))
    except:
        redirect("/")
    conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
#    player = find_player(conn, player_id)
    if template_id in ClotConfig.template_names:
        template_name = ClotConfig.template_names[template_id] 
    else:
        template_name = ClotConfig.retired_template_names[template_id]
 
    games = find_template_games(conn, template_id)
#    history = find_history_records(conn, player_id=player_id)
    
    finished_games = []
    ongoing_games = []
    for game in games:
        if game.finish_date is not None:
            finished_games.append(game)

    finished_games = sorted(finished_games, key=lambda game: game.finish_date, reverse=True)
   
    template_protip = ""
    if (template_id in ClotConfig.template_protips):
        template_protip = ClotConfig.template_protips[template_id]

    container = LOTContainer()
    return render_template('viewtemplate.html', games = finished_games, container = container, template_id = template_id, template_name = template_name, template_protip = template_protip)    
