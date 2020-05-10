"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask
from flask_compress import Compress
from waitress import serve

from mtl.clot.api import api
from mtl.clot.choose_games import choose_games_page
from mtl.clot.clan_leaderboard import clan_leaderboard_page
from mtl.clot.home import home_page
from mtl.clot.join import join_page
from mtl.clot.leaderboard import leaderboard_page
from mtl.clot.leave import leave_page
from mtl.clot.login import login_page
from mtl.clot.logout import logout_page
from mtl.clot.mtl_stats import mtl_stats_page
from mtl.clot.report import report_page
from mtl.clot.update_notable_games import update_notable_games_page
from mtl.clot.veto_templates import veto_templates_page
from mtl.clot.view_all_players import view_all_players_page
from mtl.clot.view_clan import view_clan_page
from mtl.clot.view_player import view_player_page
from mtl.clot.view_template import view_template_page


app = Flask(__name__)

# Trim all new lines and whitespaces.
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

compress = Compress()
compress.init_app(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
app.secret_key = 'sou2#z^%wi*46dt=#nfb3d_41g+uif$(koz498xdx^ll3vee_$'

# application = webapp2.WSGIApplication([
#    ('/allplayers/(\d+)', ViewAllPlayersPage),
# ], debug=True, config=config)

app.register_blueprint(api)
app.register_blueprint(home_page)
app.register_blueprint(login_page)
app.register_blueprint(logout_page)
app.register_blueprint(join_page)
app.register_blueprint(clan_leaderboard_page)
app.register_blueprint(leaderboard_page)
app.register_blueprint(leave_page)
app.register_blueprint(choose_games_page)
app.register_blueprint(mtl_stats_page)
app.register_blueprint(report_page)
app.register_blueprint(update_notable_games_page)
app.register_blueprint(veto_templates_page)
app.register_blueprint(view_clan_page)
app.register_blueprint(view_player_page)
app.register_blueprint(view_all_players_page)
app.register_blueprint(view_template_page)

if __name__ == '__main__':
    # import os
    # HOST = os.environ.get('SERVER_HOST', 'localhost')
    # PORT = 53935
    # try:
    #    PORT = int(os.environ.get('SERVER_PORT', '5555'))
    # except ValueError:
    #    PORT = 5555
    # app.run(HOST, PORT)
    serve(wsgi_app, listen='*:8080')
