#!/usr/bin/env python
# Nov 30, 2012
# Angel Joyce Torres Ramirez
# joys.tower@gmail.com
# I am not responsible for any use you give to this program, I did self-study and study purposes
# License:
# BaseMap2Image is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.


import sys
import signal
from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from functools import partial

global layer
layer = sys.argv[1]
global xMin
xMin = sys.argv[2]
global yMin
yMin = sys.argv[3]
global xMax
xMax = sys.argv[4]
global yMax
yMax = sys.argv[5]

global fileOut
fileOut = sys.argv[6]

global fileFormat
fileFormat="png"
if fileOut.find(".") != -1:
    fileFormat = fileOut.split('.')[1]
if fileFormat == "jpg":
    fileFormat = "jpeg"

timeWait = 2000
global width
width = float(sys.argv[7])
global height
height= float(sys.argv[8])

app = QApplication(sys.argv)
web = QWebView()
timerMax = QTimer()

global repaintEnd
repaintEnd = None
olResolutions = None

def onLoadFinished(result):
    global repaintEnd
    global xMin
    global yMin
    global xMax
    global yMax
    global width
    global height
    global fileOut
    global fileFormat
    
    if not result:
        print "Request failed"
        sys.exit(1)

    action = "map.zoomToExtent(new OpenLayers.Bounds("+xMin+", "+yMin+", "+xMax+", "+yMax+"), true);"
    web.page().mainFrame().evaluateJavaScript(action)

    repaintEnd = None
    pauseReq()

    img = QImage(web.page().mainFrame().contentsSize(), QImage.Format_ARGB32_Premultiplied)
    imgPainter = QPainter(img)
    web.page().mainFrame().render(imgPainter)
    imgPainter.end()
    img = img.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation )
    img.save( fileOut, fileFormat)
    sys.exit(0)
    

def pauseReq():
	global repaintEnd
	timerMax.start()
	while not repaintEnd:
		qApp.processEvents()
	timerMax.stop()


def endTimer():
	global repaintEnd
	repaintEnd = True
	
def resolutions():
	if olResolutions == None:
	  resVariant = web.page().mainFrame().evaluateJavaScript("map.layers[0].resolutions")
	  olResolutions = []
	  for res in resVariant.toList():
		olResolutions.append(res.toDouble()[0])
	return olResolutions    

timerMax.setSingleShot(True)
timerMax.setInterval(int(timeWait))
QObject.connect(timerMax, SIGNAL("timeout()"), endTimer)

web.setFixedSize(width,height)
web.connect(web, SIGNAL("loadFinished(bool)"), onLoadFinished)
pathUrl = "file:///%s/html/%s.html" % (os.getcwd(), layer)
web.load(QUrl(pathUrl))
web.show()


sys.exit(app.exec_())
