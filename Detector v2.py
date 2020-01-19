from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import socket

# User inputs the IP address of the detector
ip = str(input('Enter the IP Address.\n'))
if ip == 'a':
    ip = '192.168.15.232'
    print(ip, 'selected')

# Milliseconds between detector cps interval
interval = int(input('Enter the interval between measurements in milliseconds.\n'))

# settings to establish connection
TCP_IP = ip
TCP_PORT = 10001
BUFFER_SIZE = 1024

# Creates and opens a connections with the detector
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
# mw = QtGui.QMainWindow()
# mw.resize(800,800)

# Creates window object
win = pg.GraphicsWindow(title="He-3 Detector CPS")
win.resize(1000, 600)
win.setWindowTitle('Detector Data')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Creates a Graph object in the window object
p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='y')

data_x = []
data_y = []
ptr = 0


def update():
    global curve, data_x, data_y, ptr, p6
    s.send(b'cps\r\n')  # send command to detector
    counts_raw = str(s.recv(BUFFER_SIZE))  # receive detector data back
    counts_filtered = ''

    # Filters out non numeric characters
    for letter in counts_raw:
        if letter.isnumeric():
            counts_filtered += letter

    # adds the filtered data to the data if it is neither 0 nor empty
    if counts_filtered != '' and counts_filtered != 0:
        data_y.append(int(counts_filtered))
        data_x.append(float(ptr*interval/1000))

    # updates graph
    curve.setData(x=data_x, y=np.asarray(data_y))
    ptr += 1


# timer set to update at the given interval
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(interval)

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
