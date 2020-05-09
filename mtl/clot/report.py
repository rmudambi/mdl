from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound
from mtl.ladder.utilities.DAL import *
from mtl.clot.lot import LOTContainer


report_page = Blueprint('report_page', __name__,
                        template_folder='templates', static_folder="/static")

@report_page.route('/report')
def show():
    container = LOTContainer()

    conn = sqlite3.connect(ClotConfig.database_location)
    players = get_report(conn)
    return render_template('report.html', players = players, container = container)
