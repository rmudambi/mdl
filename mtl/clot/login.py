from flask import Blueprint, abort, redirect, request, session
from jinja2 import TemplateNotFound

from mtl.ladder.utilities.api import validate_token
from mtl.ladder.config import clot_config


login_page = Blueprint('login_page', __name__, template_folder='templates', static_folder="/static")


# This page follows the instructions at http://wiki.warlight.net/index.php/CLOT_Authentication
@login_page.route('/login')
def show():
    try:
        state = request.args.get('state')

        # If routed from home page.
        if 'clotpass' not in request.args:
            redirect_url = "http://warlight.net/CLOT/Auth?p={0}&state={1}".format(clot_config.PROFILE_ID, state)
            return redirect(redirect_url)

        # If routed from WL
        player_token = int(request.args.get('token'))
        clotpass = request.args.get('clotpass')

        api_response = validate_token(clot_config.EMAIL, clot_config.TOKEN, player_token)
        if clotpass == api_response['clotpass']:
            session['authenticatedtoken'] = player_token
        
        return redirect("/" + state)
    except TemplateNotFound as e:
        print(str(e))
        abort(404)
