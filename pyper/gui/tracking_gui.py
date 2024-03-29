# -*- coding: utf-8 -*-
"""
**************
The GUI module
**************

Creates the graphical interface


.. note::
    This module depends on importing OpenGL.GL although it doesn't uses it directly but it
    is used by the Qt interface.

:author: crousse
"""
import os
import sys

from OpenGL import GL # WARNING: Hack necessary to get qtQuick working

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon

from pyper.video.transcoder import TranscoderIface
from pyper.gui.tabs_interfaces import ViewerIface, TrackerIface, RecorderIface, CalibrationIface
from pyper.gui.code_editor import EditorIface
from pyper.gui.parameters import ParamsIface
from pyper.gui.image_providers import CvImageProvider, PyplotImageProvider
from pyper.config import conf

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


def main():
    app = QApplication(sys.argv)
    appEngine = QQmlApplicationEngine()
    context = appEngine.rootContext()
    # ALL THE ADDIMAGEPROVIDER LINES BELOW ARE REQUIRED TO MAKE QML BELIEVE THE PROVIDER IS VALID BEFORE ITS CREATION
    appEngine.addImageProvider('viewerprovider', CvImageProvider())
    appEngine.addImageProvider('trackerprovider', CvImageProvider())
    appEngine.addImageProvider('recorderprovider', CvImageProvider())
    appEngine.addImageProvider('calibrationprovider', CvImageProvider())
    appEngine.addImageProvider('transcoderprovider', CvImageProvider())

    analysis_image_provider = PyplotImageProvider(fig=None)
    appEngine.addImageProvider("analysisprovider", analysis_image_provider)
    analysis_image_provider2 = PyplotImageProvider(fig=None)
    appEngine.addImageProvider("analysisprovider2", analysis_image_provider2)
    qml_source_path = os.path.join(conf.shared_directory, 'qml', 'main', 'Pyper.qml')
    if not os.path.isfile(qml_source_path):
        raise PyperGUIError("Qml code not found at {}, please verify your installation".format(qml_source_path))
    appEngine.load(qml_source_path)  # TODO: check if QUrl(qml_source_path)
    try:
        win = appEngine.rootObjects()[0]
    except IndexError:
        raise PyperGUIError("Could not start the QT GUI")

    icon = QIcon(os.path.join(conf.shared_directory, 'resources', 'icons', 'pyper.png'))
    win.setIcon(icon)

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
    transcoder = TranscoderIface(app, context, win, params, "transcodingDisplay", "transcoderprovider")
    editor = EditorIface(app, context, win)

    context.setContextProperty('py_iface', params)
    context.setContextProperty('py_viewer', viewer)
    context.setContextProperty('py_tracker', tracker)
    context.setContextProperty('py_recorder', recorder)
    context.setContextProperty('py_calibration', calibrater)
    context.setContextProperty('py_editor', editor)
    context.setContextProperty('py_transcoder', transcoder)

    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
