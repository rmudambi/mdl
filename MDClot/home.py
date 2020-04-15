from datetime import datetime
from flask import Blueprint, render_template, abort, session
from jinja2 import TemplateNotFound
from utilities.DAL import find_player, insert_player, update_player
from utilities.api import validateToken
from lot import LOTContainer
import sqlite3
from config.ClotConfig import ClotConfig
import operator

home_page = Blueprint('home_page', __name__, template_folder='templates', static_folder="/static")


@home_page.route('/')
@home_page.route('/home')
def show():
    try:
        currentPlayer = None
        container = LOTContainer()
        if 'authenticatedtoken' in session:
            inviteToken = session['authenticatedtoken']
            conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
            currentPlayer = find_player(conn, (inviteToken))

            #Check if this invite token is new to us
            if currentPlayer is None:
                blacklisted_players = [2920026449, 9336062702, 9584375174, 732503825, 2958204123, 1840549224, 2847280410, 3040482585]
                if inviteToken in blacklisted_players:
                    return 'The supplied invite token is invalid.  You have been banned from this ladder.'

                templates = list(ClotConfig.template_names.keys())
                template_counter = 0
                while (template_counter < len(templates)):
                    end = (template_counter+15 if template_counter + 15 < len(templates)  else len(templates)-1)
                    templateIDs = ','.join(str(template) for template in templates[template_counter:end])

                    #Call the warlight API to get the name and verify that the invite token is correct. Can only check for 15 templates at a time(API restriction).
                    apiret = validateToken(ClotConfig.email, ClotConfig.token, inviteToken, templateIDs)

                    if (not "tokenIsValid" in str(apiret)) or ("CannotUseTemplate" in str(apiret)):
                        del apiret["clotpass"]
                        return 'The supplied invite token is invalid.  You have not unlocked all the templates and maps on this ladder. Error Code - ' + str(apiret)

                    template_counter += 15
        
                currentName = apiret['name']
                current_clan = None
                if 'clan' in apiret.keys(): 
                    current_clan = apiret['clan']

                player_record = (datetime.now(), currentName, inviteToken, 1500, False, False, 5, None, None, current_clan, 0, 1500, None, None, None, False)
                player = insert_player(conn, player_record)
        
                player.player_name = currentName
                player.clan = current_clan
                update_player(conn, player)

            if container.sorted_ranked_players is not None and currentPlayer is not None:
                player_rank = [i for i, player in enumerate(container.sorted_ranked_players) if player.player_id == currentPlayer.player_id]
                if len(player_rank) == 1:
                    # Add one since rank = index + 1
                    currentPlayer.rank = player_rank[0] + 1

        sorted_template_list = sorted(ClotConfig.template_names, key=lambda k: ClotConfig.template_names[k])
        sorted_retired_template_list = sorted(ClotConfig.retired_template_names, key=lambda k: ClotConfig.retired_template_names[k])
        return render_template('home.html', currentPlayer=currentPlayer, container = container, templates = ClotConfig.template_names, 
                               retired_templates = ClotConfig.retired_template_names, sorted_template_list = sorted_template_list, 
                               retired_template_list = sorted_retired_template_list)
    except TemplateNotFound as e:
        print(str(e))
        abort(404)
