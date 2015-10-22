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

DEBUG = True

class Logger(QObject):
    """
    A qml object for logging the events
    In production, the standard out is redirected to it.
    It is not meant to be interacted with directly (use print() instead)
    """
    
    def __init__(self, context, parent=None, logObjectName="log"):
        QObject.__init__(self, parent)
        self.win = parent
        self.ctx = context
        self.log = self.win.findChild(QObject, logObjectName)
    
    def write(self, text):
        """
        The method to make it compatible with sys.stdout
        The text gets printed in the corresponding qml component
        
        :param string text: The text to append at the end of the current qml component text
        """
        if text:
            previousText = self.log.property('text')
            outputText = '{}\n>>>{}'.format(previousText, text)
            self.log.setProperty('text', outputText)

if __name__ == '__main__':
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
    viewer = ViewerIface(app, context, win, params, "preview", "viewerprovider")
    tracker = TrackerIface(app, context, win, params, "trackerDisplay", "trackerprovider")
    recorder = RecorderIface(app, context, win, params, "recording", "recorderprovider")
    calibrater = CalibrationIface(app, context, win, params, "calibrationDisplay", "calibrationprovider")
    
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
