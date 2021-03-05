from . import grapher
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from humidifier.db import get_db
from datetime import (datetime, timedelta)

bp = Blueprint('panel', __name__)

@bp.route('/', methods=['GET'])
@bp.route('/panel', methods=['GET'])
def show_panel():
    timeDelta = timedelta(days=7)
    time = request.args.get('value')
    if time == 'h4':
        timeDelta = timedelta(hours=4)
    elif time == 'd1':
        timeDelta = timedelta(days=1)
    elif time == 'd3':
        timeDelta = timedelta(days=3)
    elif time == 'd7':
        timeDelta = timedelta(days=7)
    elif time == 'd30':
        timeDelta = timedelta(days=30)
    endTimePoint = datetime.now()
    startTimePoint = endTimePoint - timeDelta
    timeframe = [startTimePoint, endTimePoint]
    logsList = grapher.GetLogsInTimeframe(timeframe)
    dataPoints = grapher.CombineLogs(logsList, timeframe)
    html_str = grapher.PlotDataMPLToHTML(dataPoints)
    return render_template('panel/panel.html', panel=html_str)