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
    endTimePoint = datetime.now()
    startTimePoint = endTimePoint - timedelta(days=1)
    timeframe = [startTimePoint, endTimePoint]
    logsList = grapher.GetLogsInTimeframe(timeframe)
    dataPoints = grapher.CombineLogs(logsList, timeframe)
    html_str = grapher.PlotDataMPLToHTML(dataPoints)
    return render_template('panel/panel.html', panel=html_str)