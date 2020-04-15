from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound
from utilities.api import validateToken
from config.ClotConfig import ClotConfig


login_page = Blueprint('login_page', __name__,
                        template_folder='templates', static_folder="/static")

#This page follows the instructions at http://wiki.warlight.net/index.php/CLOT_Authentication
@login_page.route('/login')
def show():
    try:
        state = request.args.get('state')

        # If routed from home page.
        if 'clotpass' not in request.args:
            redirect_url = "http://warlight.net/CLOT/Auth?p={0}&state={1}".format(ClotConfig.profile_id, state)
            return redirect(redirect_url)

        # If routed from WL
        player_token = int(request.args.get('token'))
        clotpass = request.args.get('clotpass')

        apiret = validateToken(ClotConfig.email, ClotConfig.token, player_token)
        if clotpass == apiret['clotpass']:
            session['authenticatedtoken'] = player_token
        
        return redirect("/"+ state)
    except TemplateNotFound as e:
        print(str(e))
        abort(404)
