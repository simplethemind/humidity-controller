import serial
import os
import datetime
from flask import current_app as app

def SendStoredValues(writer):
    with open('humidifier/static/storedValues', 'r') as f:
        serialLine = ''
        while serialLine != '^':
            serialLine = f.readline()
            print('>>> ' + serialLine)
            writer.write(bytes(serialLine, 'ascii'))
            if serialLine == '^':
                break
            serialLine = ''
            while serialLine == '':
                serialLine = writer.readline().decode('utf-8')
            print('<<< ' + serialLine)
        
def SendMockValue(writer):
    serialLine = b'v0M800\n'
    writer.write(serialLine)
    writer.flush()
    print(serialLine)
    serialLine = ''
    while serialLine == '':
        serialLine = writer.readline().decode('utf-8')
    print(serialLine)


def start_monitoring():
    dir = os.listdir('/dev')

    # port = 'COM4' ### Only on PC
    ### Use this on linux systems ###
    for path in dir:
        if 'ACM' in path:
            print(path)
            port = os.path.join('/dev', path)

    reader = serial.Serial(port=port, baudrate=115200, timeout=5)
    reader.flush()
    serialLine = ''

    while not serialLine.startswith('Ready'):
        serialLine = reader.readline().decode('utf-8')

    SendStoredValues(reader)

    filename = os.path.basename(reader.name) + '_' + datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S') + '.csv'

    logsFolder = os.path.join(os.path.expanduser('~'),'humidity-monitor','logs')

    try:
        os.makedirs(logsFolder)
    except OSError:
        pass

    fullFilepath = os.path.join(logsFolder, filename)
    
    while True:
        serialLine = ''
        while serialLine == '':
            serialLine = reader.readline().decode('utf-8').rstrip()
        timestampLine = datetime.datetime.now().strftime('%x %X')
        print(timestampLine + ',' + serialLine)
        if not os.path.exists(fullFilepath):
            with open(fullFilepath, 'x') as f:
                pass
        with open(fullFilepath, 'a') as f:
            f.write(timestampLine + "," + serialLine + '\r\n')

if __name__ == '__main__':
    start_monitoring()
