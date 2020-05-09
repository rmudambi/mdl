from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound, filters
from mtl.ladder.utilities.DAL import find_player, insert_notable_game, delete_notable_games, find_game
import sqlite3
from mtl.ladder.config.ClotConfig import ClotConfig
from datetime import datetime


update_notable_games_page = Blueprint('update_notable_games_page', __name__,
                        template_folder='templates', static_folder="/static")

@update_notable_games_page.route('/updatenotablegames')
def show():
    if 'authenticatedtoken' not in session:
        return redirect('/')

    conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
    #Find the player by their token
    player_id = session['authenticatedtoken']
    player = find_player(conn, player_id)

    param_notable_games = request.args.get('gameIds')
    if not param_notable_games:
        # No notable games selected. 
        # Flush existing notable games before inserting new ones.
        delete_notable_games(conn, player_id)
    else:
        new_notable_games = [int(game_id) for game_id in param_notable_games.split(",")]
        if len(new_notable_games) > ClotConfig.notable_game_count:
            return "Only " + ClotConfig.notable_game_count + " notable games permitted."

        for game_id in new_notable_games:
            game = find_game(conn, game_id)
            if game is None or game.finish_date is None or not(game.team_a == player_id or game.team_b == player_id):
                return "You can only choose finished games you have played on MTL."

        # Flush existing notable games before inserting new ones.
        delete_notable_games(conn, player_id)
        current_time = datetime.now()
        for game_id in new_notable_games:
            notable_game_record = (current_time, player_id, game_id)
            insert_notable_game(conn, notable_game_record)
    
    redirect_url = "/player?playerId={0}".format(player_id)
    return redirect(redirect_url)
