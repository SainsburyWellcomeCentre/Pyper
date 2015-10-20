# -*- coding: utf-8 -*-
"""
**************
The GUI module
**************

Creates the graphical interface

.. note:: This module depends on importing OpenGL.GL although it doens't uses it directly

:author: crousse
"""

import sys


from OpenGL import GL # Hack necessary to get qtQuick working

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QUrl

from gui_interfaces import ParamsIface, ViewerIface, TrackerIface, RecorderIface, CalibrationIface
from image_providers import CvImageProvider, PyplotImageProvider

DEBUG = False

class Logger(QObject):
    
    def __init__(self, context, parent=None, logObjectName="log"):
        QObject.__init__(self, parent)
        self.win = parent
        self.ctx = context
        self.log = self.win.findChild(QObject, logObjectName)
    
    def write(self, text):
        if text:
            previousText = self.log.property('text')
            outputText = '{}\n>>>{}'.format(previousText, text)
            self.log.setProperty('text', outputText)

def main():
    app = QApplication(sys.argv)
    
    appEngine = QQmlApplicationEngine()
    
    context = appEngine.rootContext()
    appEngine.addImageProvider('viewerprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('trackerprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('recorderprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('calibrationprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('analysisprovider', PyplotImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('analysisprovider2', PyplotImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.load(QUrl('./qml/MouseTracker.qml'))
    
    win = appEngine.rootObjects()[0]
    
    if not DEBUG:
        logger = Logger(context, win, "log")
        sys.stdout = logger
    
    # REGISTER PYTHON CLASSES WITH QML
    params = ParamsIface(app, context, win)
    viewer = ViewerIface(app, context, win, params)
    tracker = TrackerIface(app, context, win, params)
    recorder = RecorderIface(app, context, win, params)
    calibrater = CalibrationIface(app, context, win, params)
    
    context.setContextProperty('py_iface', params)
    context.setContextProperty('py_viewer', viewer)
    context.setContextProperty('py_tracker', tracker)
    context.setContextProperty('py_recorder', recorder)
    context.setContextProperty('py_calibration', calibrater)
    
    win.show()
    try:
        apcode = app.exec_()
    except:
        print('there was an issue')
    finally:
        sys.exit(apcode)

if __name__ == '__main__':
    main()
