from random import randint

from flask import redirect, request, session, Blueprint
import sqlite3

from mtl.ladder.config import clot_config
from mtl.ladder.utilities.dal import find_player, update_player

choose_games_page = Blueprint('choose_games_page', __name__, template_folder='templates', static_folder="/static")


@choose_games_page.route('/choice')
def show():
    player_id = int(request.args.get('playerId'))
    max_games = request.args.get('numberOfGames')

    if player_id in clot_config.BLACKLISTED_PLAYERS:
        return 'The supplied invite token is invalid.  You have been banned from this ladder.'

    if 'authenticatedtoken' not in session:
        return redirect('/')

    conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM

    # Find the player by their token
    player_token = session['authenticatedtoken']
    player = find_player(conn, player_token)

    # Redirect if not the logged in user
    if player.player_id != player_id:
        return redirect('/')

    if max_games:
        game_count = int(max_games)
        if game_count < 2 or game_count > 9:
            game_count = 5
        player.max_games = game_count
        player.is_joined = True

        # Make the player wait for a random number of update cycles before allowing them to receive new games.
        # This prevents gaming the ladder by increasing game count to pick specific opponents.
        player.wait_cycles = randint(1, 3)
        update_player(conn, player)
        
    return redirect('/player?playerId=' + str(player_id))
