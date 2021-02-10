from dash import Dash
import dash_html_components as html
from humidifier.db import get_db
from datetime import (datetime, timedelta)
import dash_core_components as dcc
from . import grapher
from flask import current_app, g
from flask.cli import with_appcontext

def serve_layout():
    endTimePoint = datetime.now()
    startTimePoint = endTimePoint - timedelta(days=1)
    timeframe = [startTimePoint, endTimePoint]
    logsList = grapher.GetLogsInTimeframe(timeframe)
    dataPoints = grapher.CombineLogs(logsList, timeframe)
    figure = grapher.PlotData(dataPoints)
    html_graph = html.Div([dcc.Graph(figure=figure)])
    return html_graph

def init_dashboard(server):
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dash/',
        external_stylesheets=[
            '/static/styles.css',
        ]
    )


    # Create Dash Layout
    dash_app.layout = serve_layout

    init_callbacks(dash_app)

    return dash_app.server

def init_callbacks(dash_app):
    pass
