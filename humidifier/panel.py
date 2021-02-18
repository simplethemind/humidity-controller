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

@bp.route('/', methods=['GET', 'POST'])
def show_panel():
    timeDelta = timedelta(days=7)
    if request.method == 'POST':
        if '1/6day' in request.form:
            timeDelta = timedelta(hours=4)
        if '1day' in request.form:
            timeDelta = timedelta(days=1)
        elif '3days' in request.form:
            timeDelta = timedelta(days=3)
        elif '7days' in request.form:
            timeDelta = timedelta(days=7)
        elif '30days' in request.form:
            timeDelta = timedelta(days=30)
    endTimePoint = datetime.now()
    startTimePoint = endTimePoint - timeDelta
    timeframe = [startTimePoint, endTimePoint]
    logsList = grapher.GetLogsInTimeframe(timeframe)
    dataPoints = grapher.CombineLogs(logsList, timeframe)
    html_str = grapher.PlotDataMPLToHTML(dataPoints)
    return render_template('panel/panel.html', panel=html_str)