import os
from numpy.core.function_base import logspace
import pandas
import glob
import numpy
import datetime
import re
import plotly.express as px
from flask import current_app as app

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

def customLegend(fig, nameSwap):
    for i, dat in enumerate(fig.data):
        for elem in dat:
            if elem == 'name':
                print(fig.data[i].name)
                fig.data[i].name = nameSwap[fig.data[i].name]
    return(fig)
    
def PlotData(dataPoints):
    if len(dataPoints) == 0:
        return None
    fig = px.line(
        dataPoints, x=0, y=[1,2,3],
        title='Umiditatea solului',
        width=900, height=600,
        labels={'value':'Procent','variable':'Plante'})
    fig.update_layout(
        yaxis_range=[0,100],
        xaxis_title='',
        yaxis_title='')
    return customLegend(fig, {'1':'Menta','2':'Yucca','3':'Gol'})

if __name__ == '__main__':
    endTimePoint = datetime.datetime.now()
    startTimePoint = endTimePoint - datetime.timedelta(hours=1)
    timeframe = [startTimePoint, endTimePoint]
    logsList = GetLogsInTimeframe(timeframe)
    dataPoints = CombineLogs(logsList, timeframe)
    figure = PlotData(dataPoints)
    figure.show()