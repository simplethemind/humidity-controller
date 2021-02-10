import serial
import os
import datetime
from flask import current_app as app

def start_monitoring():
    dir = os.listdir('/dev')

    port = ''
    for path in dir:
        if 'ACM' in path:
            print(path)
            port = os.path.join('/dev', path)

    reader = serial.Serial(port=port, baudrate=9600, timeout=1)
    reader.flush()

    filename = os.path.basename(reader.name) + '_' + datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S') + '.csv'

    logsFolder = os.path.join(os.path.expanduser('~'),'humidity-monitor','logs')

    try:
        os.makedirs(logsFolder)
    except OSError:
        pass

    fullFilepath = os.path.join(logsFolder, filename)
    with open(fullFilepath, 'x') as f:
        pass
    
    while True:
        if reader.in_waiting > 0:
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
