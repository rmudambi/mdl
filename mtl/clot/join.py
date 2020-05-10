from datetime import datetime

from flask import abort, redirect, render_template, session, Blueprint
from jinja2 import TemplateNotFound
import sqlite3

from mtl.clot.lot import LOTContainer
from mtl.ladder.config import clot_config
from mtl.ladder.utilities.api import validate_token
from mtl.ladder.utilities.dal import find_player, insert_player, update_player

join_page = Blueprint('join_page', __name__, template_folder='templates', static_folder="/static")


@join_page.route('/join')
def show():
    try:
        if 'authenticatedtoken' not in session:
            return redirect("/login?state=join")

        player_token = session['authenticatedtoken']

        if player_token in clot_config.BLACKLISTED_PLAYERS:
            return 'The supplied invite token is invalid.  You have been banned from this ladder.'

        templates = list(clot_config.TEMPLATE_NAMES.keys())
        template_counter = 0
        api_response = {}
        while template_counter < len(templates):
            end = (template_counter + 15 if template_counter + 15 < len(templates) else len(templates) - 1)
            template_ids = ','.join(str(template) for template in templates[template_counter:end])

            # Call the Warlight API to get the name and verify that the invite token is correct.
            # Can only check for 15 templates at a time(API restriction).
            api_response = validate_token(clot_config.EMAIL, clot_config.TOKEN, player_token, template_ids)

            if ("tokenIsValid" not in str(api_response)) or ("CannotUseTemplate" in str(api_response)):
                del api_response["clotpass"]
                return (f'The supplied invite token is invalid.  You have not unlocked all the templates and maps on '
                        f'this ladder. Error Code - {str(api_response)}')

            template_counter += 15
        
        current_name = api_response['name'] if 'name' in api_response.keys else None
        current_clan = api_response['clan'] if 'clan' in api_response.keys else None

        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
        # Check if this invite token is new to us
        player = find_player(conn, player_token)
        if player is None:
            player_record = (datetime.now(), current_name, player_token, 1500, False, True, 5, None, None,
                             current_clan, 0, 1500, None, None, None, False)
            player = insert_player(conn, player_record)
        
        player.player_name = current_name
        player.clan = current_clan
        player.is_joined = True
        update_player(conn, player)

        # Update container with latest players
        container = LOTContainer()
        return render_template('join.html', container=container, current_player=player)
    except TemplateNotFound as e:
        print(str(e))
        abort(404)
