from . import grapher
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from humidifier.db import get_db
from datetime import (datetime, timedelta)
import dash_core_components as dcc
import dash_html_components as html

bp = Blueprint('panel', __name__)

@bp.route('/')
def show_panel():
    return render_template('panel/panel.html')