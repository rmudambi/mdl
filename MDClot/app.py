"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template
from api import api
from home import home_page
from login import login_page
from logout import logout_page
from join import join_page
from clanleaderboard import clan_leaderboard_page
from leaderboard import leaderboard_page
from leave import leave_page
from choosegames import choose_games_page
from mdlstats import mdl_stats_page
from report import report_page
from updatenotablegames import update_notable_games_page
from vetotemplates import veto_templates_page
from viewclan import view_clan_page
from viewplayer import view_player_page
from viewallplayers import view_all_players_page
from viewtemplate import view_template_page
from waitress import serve
from flask_compress import Compress


app = Flask(__name__)

# Trim all new lines and whitespaces.
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

compress = Compress()
compress.init_app(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
app.secret_key = 'sou2#z^%wi*46dt=#nfb3d_41g+uif$(koz498xdx^ll3vee_$'

#application = webapp2.WSGIApplication([
#    ('/allplayers/(\d+)', ViewAllPlayersPage),
#], debug=True, config=config)

app.register_blueprint(api)
app.register_blueprint(home_page)
app.register_blueprint(login_page)
app.register_blueprint(logout_page)
app.register_blueprint(join_page)
app.register_blueprint(clan_leaderboard_page)
app.register_blueprint(leaderboard_page)
app.register_blueprint(leave_page)
app.register_blueprint(choose_games_page)
app.register_blueprint(mdl_stats_page)
app.register_blueprint(report_page)
app.register_blueprint(update_notable_games_page)
app.register_blueprint(veto_templates_page)
app.register_blueprint(view_clan_page)
app.register_blueprint(view_player_page)
app.register_blueprint(view_all_players_page)
app.register_blueprint(view_template_page)

if __name__ == '__main__':
    #import os
    #HOST = os.environ.get('SERVER_HOST', 'localhost')
    #PORT = 53935 
    #try:
    #    PORT = int(os.environ.get('SERVER_PORT', '5555'))
    #except ValueError:
    #    PORT = 5555
    #app.run(HOST, PORT)
    serve(wsgi_app, listen='*:8080')

