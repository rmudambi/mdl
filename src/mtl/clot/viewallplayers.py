from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound
from lot import LOTContainer


view_all_players_page = Blueprint('view_all_players_page', __name__,
                        template_folder='templates', static_folder="/static")

@view_all_players_page.route('/allplayers')
def show():
    container = LOTContainer()
    return render_template('viewallplayers.html', container = container)
