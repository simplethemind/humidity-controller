import os
import matplotlib
from mpld3.plugins import MousePosition
from numpy.core.function_base import logspace
import pandas
import glob
import numpy
import datetime
import re
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from flask import current_app as app
from mpld3 import fig_to_html, plugins

def GetLogsInTimeframe(timeframe):
    start = timeframe[0]
    end = timeframe[1]
    logsFolder = os.path.join(os.path.expanduser('~'),'humidity-monitor','logs','*.csv')
    allLogs = glob.glob(logsFolder)
    allLogs.sort(reverse=True)
    validLogs = []
    for log in allLogs:
        logDateString = re.search('(\d{4}\.\d{2}\.\d{2}_\d{2}\.\d{2}\.\d{2})', log)
        logDate = datetime.datetime.strptime(logDateString[0], '%Y.%m.%d_%H.%M.%S')
        if logDate < end and logDate > start:
            if os.path.getsize(log) > 0:
                validLogs.append(log)
                continue
        if logDate < start:
            if os.path.getsize(log) > 0:
                validLogs.append(log)
                break
    validLogs.sort()
    return validLogs

def CombineLogs(logs, timeframe):
    npArrayList = []
    for file in logs:
        logDataFrame = pandas.read_csv(
            file, sep=',', 
            header=None, 
            index_col=None
        )
        npArrayList.append(logDataFrame)
    combinedArray = numpy.vstack(npArrayList)
    # filter out extraneous values
    start = 0
    testDate = datetime.datetime.strptime(combinedArray[start][0], '%m/%d/%y %H:%M:%S')
    while testDate < timeframe[0]:
        start += 1
        if start>len(combinedArray)-1:
            return []
        testDate = datetime.datetime.strptime(combinedArray[start][0], '%m/%d/%y %H:%M:%S')
    end = len(combinedArray) - 1
    testDate = datetime.datetime.strptime(combinedArray[end][0], '%m/%d/%y %H:%M:%S')
    while testDate > timeframe[1]:
        end -= 1
        testDate = datetime.datetime.strptime(combinedArray[end][0], '%m/%d/%y %H:%M:%S')
    validarray = combinedArray[start:end + 1]
    return validarray

# def customLegend(fig, nameSwap):
#     for i, dat in enumerate(fig.data):
#         for elem in dat:
#             if elem == 'name':
#                 fig.data[i].name = nameSwap[fig.data[i].name]
#     return(fig)
    
# def PlotData(dataPoints):
#     if len(dataPoints) == 0:
#         return None
#     fig = px.line(
#         dataPoints, x=0, y=[1,2,3],
#         title='Umiditatea solului',
#         width=900, height=600,
#         labels={'value':'Procent','variable':'Plante'})
#     fig.update_layout(
#         yaxis_range=[0,100],
#         xaxis_title='',
#         yaxis_title='')
#     return customLegend(fig, {'1':'Menta','2':'Yucca','3':'Gol'})

def ExtractPointPosition(pointData):
    ydata = [i for i in pointData.get_ydata()]
    xdata = [i for i in pointData.get_xdata()]
    fdata = [(ydata[i], xdata[i]) for i in range(len(ydata))]
    stringData = ['humidity: {0}\ntime: {1}'.format(dataInfo[0], datetime.datetime.strftime(dates.num2date(dataInfo[1]), '%Y/%m/%d %H:%M:%S')) for dataInfo in fdata]
    return stringData

def PlotDataMPLToHTML(dataPoints):
    swap = numpy.swapaxes(dataPoints, 0, 1)
    timescale = [datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S') for date in swap[0]]
    dates = matplotlib.dates.date2num(timescale)
    fig, ax = plt.subplots()
    plt.rcParams.update({'figure.autolayout': True})
    p1 = ax.plot_date(dates, swap[1], color='red', linestyle='solid', marker=',', markersize='4', label='Mentă')
    p2 = ax.plot_date(dates, swap[2], color='green', linestyle='solid', marker=',', markersize='4', label='Yucca')
    p3 = ax.plot_date(dates, swap[3], color='blue', linestyle='solid', marker=',', markersize='4', label='Gol')
    ax.legend()
    xlabels = ax.get_xticklabels()
    plt.setp(xlabels, rotation=30, horizontalalignment='right')
    ax.set(ylim=[0, 100], xlabel='Dată', ylabel='Procent (%)', title='Grafic umiditate plante')

    # Create HTML
    plugins.clear(fig)
    tooltip_plugin1 = plugins.PointLabelTooltip(p1[0], ExtractPointPosition(p1[0]))
    tooltip_plugin2 = plugins.PointLabelTooltip(p2[0], ExtractPointPosition(p2[0]))
    tooltip_plugin3 = plugins.PointLabelTooltip(p3[0], ExtractPointPosition(p3[0]))
    plugins.connect(fig, tooltip_plugin1, tooltip_plugin2, tooltip_plugin3, plugins.Zoom(), plugins.Reset())
    html_str = fig_to_html(fig)
    return html_str

if __name__ == '__main__':
    endTimePoint = datetime.datetime.now() - datetime.timedelta(days=7)
    startTimePoint = endTimePoint - datetime.timedelta(days=5)
    timeframe = [startTimePoint, endTimePoint]
    logsList = GetLogsInTimeframe(timeframe)
    dataPoints = CombineLogs(logsList, timeframe)
    # figure = PlotData(dataPoints)
    # figure.show()
    html_str = PlotDataMPLToHTML(dataPoints)
    with open('index.html', 'w') as f:
        f.write(html_str)
