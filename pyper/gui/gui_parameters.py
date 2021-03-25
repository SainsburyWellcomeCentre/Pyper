import os
import sys
from skimage.io import imread

from PyQt5.QtCore import QObject, pyqtSlot, Qt, QVariant, pyqtSignal, pyqtProperty
from PyQt5.QtWidgets import QFileDialog

from pyper.config.parameters import Parameters
from pyper.gui.tabs_interfaces import TRACKER_CLASSES, VIDEO_FILTERS, VIDEO_FORMATS
from pyper.utilities.utils import un_file


class GuiParameters(QObject, Parameters):
    """
    The QObject derived class that stores most of the parameters from the graphical interface
    for the other QT interfaces
    """
    def __init__(self, app, context, parent):
        """
        :param app: The QT application
        :param context:
        :param parent: the parent window
        """
        Parameters.__init__(self)
        QObject.__init__(self, parent)
        self.app = app  # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context

        self.src_path = ''
        self.dest_path = ''

        self.calib = None
        self.tracker_class = TRACKER_CLASSES["GuiTracker"]

        self._curve_update_period = self.config['gui']['update_period']

        self.ref = None

        self.min_threshold_rgb = [(0, 0, 0)] * 2  # FIXME: initialise better and append on new structure added
        self.max_threshold_rgb = [(255, 255, 255)] * 2

        self.thresholding_mode = "simple"

    def __del__(self):
        """
        Reset the standard out on destruction
        """
        sys.stdout = sys.__stdout__

    curve_update_period_signal = pyqtSignal()
    @pyqtProperty(int, notify=curve_update_period_signal)
    def curve_update_period(self):
        return self._curve_update_period

    @curve_update_period.setter
    def curve_update_period(self, period):
        self._curve_update_period = period
        self.config['gui']['update_period'] = period


    @pyqtSlot(str)
    def set_thresholding_type(self, thresholding_type):
        print("Thresholding type to be set: " + thresholding_type)
        if thresholding_type.lower() == 'hsv':
            self.set_tracker_type()

    @pyqtSlot()
    def write_defaults(self):
        """
        Writes defaults to the config file
        """
        self.config.write()

    @pyqtSlot(str)
    def set_tracker_type(self, tracker_type):
        try:
            self.tracker_class = TRACKER_CLASSES[tracker_type]
        except KeyError:
            print("Type must be one of {}, got: {}".format(TRACKER_CLASSES.keys(), tracker_type))

    @pyqtSlot()
    def chg_cursor(self):
        self.app.setOverrideCursor(Qt.CursorShape(Qt.CrossCursor))

    @pyqtSlot()
    def restore_cursor(self):
        self.app.restoreOverrideCursor()

    @pyqtSlot(result=QVariant)
    def open_video(self):
        """The QT dialog to select the video to be used for preview or tracking"""
        if hasattr(self, 'src_path'):  # FIXME: should check vs None
            src_dir = os.path.dirname(self.src_path)
        else:
            src_dir = os.getenv('HOME')
        diag = QFileDialog()
        path = diag.getOpenFileName(parent=diag,
                                    caption='Open file',
                                    directory=src_dir,
                                    filter=VIDEO_FILTERS)
        src_path = path[0]
        if src_path:
            self.src_path = src_path
            self._set_defaults()
            return src_path

    @pyqtSlot(QVariant, result=QVariant)
    def set_save_path(self, path):
        """
        The QT dialog to select the path to save the recorded video
        """
        diag = QFileDialog()
        if not path:
            path = diag.getSaveFileName(parent=diag,
                                        caption='Save file',
                                        directory=os.getenv('HOME'),
                                        filter=VIDEO_FILTERS,
                                        initialFilter="Videos (*.avi)")
            dest_path = path[0]
        else:
            dest_path = path if (os.path.splitext(path)[1] in VIDEO_FORMATS) else ""
        if dest_path:
            self.dest_path = dest_path
            return dest_path

    @pyqtSlot(str)
    def set_ref_source(self, ref_path):
        ref_path = un_file(ref_path)
        self.ref = imread(ref_path)


    @pyqtSlot(result=QVariant)
    def is_path_selected(self):
        return hasattr(self, "src_path") and self.src_path

    @pyqtSlot(result=QVariant)
    def get_path(self):
        return self.src_path if self.is_path_selected() else ""

    @pyqtSlot(result=QVariant)
    def get_file_name(self):
        path = self.get_path()
        return os.path.basename(path) if path else ""

    @pyqtSlot(result=QVariant)
    def get_dest_path(self):
        return self.dest_path if hasattr(self, "dest_path") else ""

    @pyqtSlot(int, int, int, int)
    def set_min_threshold(self, struct_idx, r, g, b):
        self.min_threshold_rgb[struct_idx] = (r, g, b)

    @pyqtSlot(int, int, int, int)
    def set_max_threshold(self, struct_idx, r, g, b):
        self.max_threshold_rgb[struct_idx] = (r, g, b)
