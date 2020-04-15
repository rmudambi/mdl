from flask import Blueprint, render_template, abort, session, redirect, Response
from jinja2 import TemplateNotFound
from utilities.DAL import find_player, insert_player, update_player
from utilities.api import validateToken
from entities.Player import Player
from lot import LOTContainer
from config.ClotConfig import ClotConfig
from datetime import datetime
import json
import sqlite3

join_page = Blueprint('join_page', __name__,
                        template_folder='templates', static_folder="/static")


@join_page.route('/join')
def show():
    try:
        if 'authenticatedtoken' not in session:
            return redirect("/login?state=join")

        container = LOTContainer()
        player_token = session['authenticatedtoken']

        blacklisted_players = [2920026449, 9336062702, 9584375174, 732503825, 2958204123, 1840549224, 2847280410, 3040482585]
        if player_token in blacklisted_players:
            return 'The supplied invite token is invalid.  You have been banned from this ladder.'

        templates = list(ClotConfig.template_names.keys())
        template_counter = 0
        while (template_counter < len(templates)):
            end = (template_counter+15 if template_counter + 15 < len(templates)  else len(templates)-1)
            templateIDs = ','.join(str(template) for template in templates[template_counter:end])            

            #Call the warlight API to get the name and verify that the invite token is correct. Can only check for 15 templates at a time(API restriction).
            apiret = validateToken(ClotConfig.email, ClotConfig.token, player_token, templateIDs)

            if (not "tokenIsValid" in str(apiret)) or ("CannotUseTemplate" in str(apiret)):
                del apiret["clotpass"]
                return 'The supplied invite token is invalid.  You have not unlocked all the templates and maps on this ladder. Error Code - ' + str(apiret)

            template_counter += 15
        
        currentName = apiret['name']

        current_clan = None
        if 'clan' in apiret.keys(): 
            current_clan = apiret['clan']

        conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
        #Check if this invite token is new to us
        player = find_player(conn, player_token)
        if player is None:
            player_record = (datetime.now(), currentName, player_token, 1500, False, True, 5, None, None, current_clan, 0, 1500, None, None, None, False)
            player = insert_player(conn, player_record)
        
        player.player_name = currentName
        player.clan = current_clan
        player.is_joined = True
        update_player(conn, player)

        # Update container with latest players
        container = LOTContainer()
        return render_template('join.html', container = container, current_player = player)
    except TemplateNotFound as e:
        print(str(e))
        abort(404)

