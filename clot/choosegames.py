from flask import Blueprint, render_template, abort, session, redirect, request
from jinja2 import TemplateNotFound
from utilities.DAL import find_player, update_player
import sqlite3
from config.ClotConfig import ClotConfig
from random import randint

choose_games_page = Blueprint('choose_games_page', __name__,
                        template_folder='templates', static_folder="/static")

@choose_games_page.route('/choice')
def show():
    player_id = int(request.args.get('playerId'))
    max_games = request.args.get('numberOfGames')

    blacklisted_players = [2920026449, 9336062702, 9584375174, 732503825, 2958204123, 1840549224, 2847280410, 3040482585]
    if player_id in blacklisted_players:
        return 'The supplied invite token is invalid.  You have been banned from this ladder.'

    if 'authenticatedtoken' not in session:
        return redirect('/')

    conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM

    #Find the player by their token
    player_token = session['authenticatedtoken']
    player = find_player(conn, player_token)

    # Redirect if not the logged in user
    if player.player_id != player_id :
        return redirect('/')

    if max_games != None:
        game_count = int(max_games)
        if game_count < 2 or game_count > 9:
            game_count = 5
        player.max_games = game_count
        player.is_joined = True

        # Make the player wait for a random number of update cycles before allowing them to receive new games.
        # This prevents gaming the ladder by increasing game count to pick specific opponents.
        player.wait_cycles = randint(1,3)
        update_player(conn, player)
        
    return redirect('/player?playerId=' + str(player_id))