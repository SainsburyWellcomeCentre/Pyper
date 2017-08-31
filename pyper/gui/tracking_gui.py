# -*- coding: utf-8 -*-
"""
**************
The GUI module
**************

Creates the graphical interface

.. note:: This module depends on importing OpenGL.GL although it doens't uses it directly

:author: crousse
"""
import os
import sys

sys.path.append(os.path.abspath("./"))  # FIXME: to be done by setup.py

from OpenGL import GL # Hack necessary to get qtQuick working

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtGui import QIcon

from pyper.gui.gui_interfaces import ParamsIface, ViewerIface, TrackerIface, RecorderIface, CalibrationIface, \
    EditorIface
from pyper.gui.image_providers import CvImageProvider, PyplotImageProvider

from pyper.exceptions.exceptions import PyperGUIError

DEBUG = True


class Logger(QObject):
    """
    A qml object for logging the events
    In production, the standard out is redirected to it.
    It is not meant to be interacted with directly (use print() instead)
    """
    
    def __init__(self, context, parent=None, log_object_name="log"):
        QObject.__init__(self, parent)
        self.win = parent
        self.ctx = context
        self.log = self.win.findChild(QObject, log_object_name)
    
    def write(self, text):
        """
        The method to make it compatible with sys.stdout
        The text gets printed in the corresponding qml component
        
        :param string text: The text to append at the end of the current qml component text
        """
        if text:
            previous_text = self.log.property('text')
            output_text = '{}\n>>>{}'.format(previous_text, text)
            self.log.setProperty('text', output_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    appEngine = QQmlApplicationEngine()
    
    context = appEngine.rootContext()
    appEngine.addImageProvider('viewerprovider', CvImageProvider())  # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('trackerprovider', CvImageProvider())  # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('recorderprovider', CvImageProvider())  # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('calibrationprovider', CvImageProvider())  # Hack to make qml believe provider is valid before its creation
    
    analysis_image_provider = PyplotImageProvider(fig=None)
    appEngine.addImageProvider("analysisprovider", analysis_image_provider)
    analysis_image_provider2 = PyplotImageProvider(fig=None)
    appEngine.addImageProvider("analysisprovider2", analysis_image_provider2)
    appEngine.load(QUrl('./pyper/qml/MouseTracker.qml'))  # FIXME: should be independant of start location (maybe location of file not start location)

    try:
        win = appEngine.rootObjects()[0]
    except IndexError:
        raise PyperGUIError("Could not start the QT GUI")

    ico = QIcon('./resources/icons/pyper.png')
    win.setIcon(ico)
    
    if not DEBUG:
        logger = Logger(context, win, "log")
        sys.stdout = logger
    
    # REGISTER PYTHON CLASSES WITH QML
    params = ParamsIface(app, context, win)
    viewer = ViewerIface(app, context, win, params, "preview", "viewerprovider")
    tracker = TrackerIface(app, context, win, params, "trackerDisplay", "trackerprovider",
                           analysis_image_provider, analysis_image_provider2)
    recorder = RecorderIface(app, context, win, params, "recording", "recorderprovider",
                             analysis_image_provider, analysis_image_provider2)
    calibrater = CalibrationIface(app, context, win, params, "calibrationDisplay", "calibrationprovider")
    editor = EditorIface(app, context, win)
    
    context.setContextProperty('py_iface', params)
    context.setContextProperty('py_viewer', viewer)
    context.setContextProperty('py_tracker', tracker)
    context.setContextProperty('py_recorder', recorder)
    context.setContextProperty('py_calibration', calibrater)
    context.setContextProperty('py_editor', editor)
    
    win.show()

    sys.exit(app.exec_())

