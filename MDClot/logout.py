from flask import Blueprint, abort, redirect, render_template, request, session
from jinja2 import TemplateNotFound


logout_page = Blueprint('logout_page', __name__, template_folder='templates', static_folder="/static")


# This page follows the instructions at http://wiki.warlight.net/index.php/CLOT_Authentication
@logout_page.route('/logout')
def show():
    try:
        session.clear()
        return redirect("/")
    except TemplateNotFound as e:
        print(str(e))
        abort(404)
