import os
import sys
from skimage.io import imread

from PyQt5.QtCore import QObject, pyqtSlot, Qt, QVariant
from PyQt5.QtWidgets import QFileDialog

from pyper.gui.tabs_interfaces import TRACKER_CLASSES, VIDEO_FILTERS, VIDEO_FORMATS
from pyper.config import conf
from pyper.utilities.utils import un_file

config = conf.config


class ParamsIface(QObject):
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
        QObject.__init__(self, parent)
        self.app = app  # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context

        self.src_path = ''
        self.dest_path = ''

        self.calib = None
        self.tracker_class = TRACKER_CLASSES["GuiTracker"]

        self.ref = None

        self._set_defaults()

    def _set_defaults(self):
        """
        Reset the parameters to default.
        To customise the defaults, users should do this in the config file.
        """
        self.bg_frame_idx = config['tracker']['frames']['ref']
        self.n_bg_frames = config['tracker']['sd_mode']['n_background_frames']
        self.start_frame_idx = self.bg_frame_idx + self.n_bg_frames
        self.end_frame_idx = config['tracker']['frames']['end']

        self.detection_threshold = config['tracker']['detection']['threshold']
        self.objects_min_area = config['tracker']['detection']['min_area']
        self.objects_max_area = config['tracker']['detection']['max_area']
        self.teleportation_threshold = config['tracker']['detection']['teleportation_threshold']

        self.n_sds = config['tracker']['sd_mode']['n_sds']

        self.clear_borders = config['tracker']['checkboxes']['clear_borders']
        self.normalise = config['tracker']['checkboxes']['normalise']
        self.extract_arena = config['tracker']['checkboxes']['extract_arena']
        self.infer_location = config['tracker']['checkboxes']['infer_location']

        self.timer_period = config['global']['timer_period']

    def __del__(self):
        """
        Reset the standard out on destruction
        """
        sys.stdout = sys.__stdout__

    @pyqtSlot(int)
    def set_timer_period(self, timer_period):
        self.timer_period = timer_period

    @pyqtSlot(result=int)
    def get_timer_period(self):
        return self.timer_period
        
    @pyqtSlot(str)
    def set_ref_source(self, ref_path):
        ref_path = un_file(ref_path)
        self.ref = imread(ref_path)

    @pyqtSlot()
    def write_defaults(self):
        """
        Writes defaults to the config file
        """
        config.write()

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

    # BOOLEAN OPTIONS
    @pyqtSlot(bool)
    def set_clear_borders(self, status):
        self.clear_borders = status
        config['tracker']['checkboxes']['clear_borders'] = status

    @pyqtSlot(result=bool)
    def get_clear_borders(self):
        return self.clear_borders

    @pyqtSlot(bool)
    def set_normalise(self, status):
        self.normalise = status
        config['tracker']['checkboxes']['normalise'] = status

    @pyqtSlot(result=bool)
    def get_normalise(self):
        return self.normalise

    @pyqtSlot(bool)
    def set_extract_arena(self, status):
        self.extract_arena = status
        config['tracker']['checkboxes']['extract_arena'] = status

    @pyqtSlot(result=bool)
    def get_extract_arena(self):
        return self.extract_arena

    @pyqtSlot(bool)
    def set_infer_location(self, status):
        self.infer_location = status
        config['tracker']['checkboxes']['infer_location'] = status

    @pyqtSlot(result=bool)
    def get_infer_location(self):
        return self.infer_location

    # DETECTION OPTIONS
    @pyqtSlot(result=QVariant)
    def get_detection_threshold(self):
        return self.detection_threshold

    @pyqtSlot(QVariant)
    def set_detection_threshold(self, threshold):
        self.detection_threshold = int(threshold)
        config['tracker']['detection']['threshold'] = int(threshold)

    @pyqtSlot(result=QVariant)
    def get_min_area(self):
        return self.objects_min_area

    @pyqtSlot(QVariant)
    def set_min_area(self, area):
        self.objects_min_area = int(area)
        config['tracker']['detection']['min_area'] = int(area)

    @pyqtSlot(result=QVariant)
    def get_max_area(self):
        return self.objects_max_area

    @pyqtSlot(QVariant)
    def set_max_area(self, area):
        self.objects_max_area = int(area)
        config['tracker']['detection']['max_area'] = int(area)

    @pyqtSlot(result=QVariant)
    def get_max_movement(self):
        return self.teleportation_threshold

    @pyqtSlot(QVariant)
    def set_max_movement(self, movement):
        self.teleportation_threshold = int(movement)
        config['tracker']['detection']['teleportation_threshold'] = int(movement)

    @pyqtSlot(result=QVariant)
    def get_n_sds(self):
        return self.n_sds

    @pyqtSlot(QVariant)
    def set_n_sds(self, n_sds):
        self.n_sds = int(n_sds)
        config['tracker']['sd_mode']['n_sds'] = int(n_sds)

    # FRAME OPTIONS
    @pyqtSlot(QVariant)
    def set_bg_frame_idx(self, idx):
        self.bg_frame_idx = int(idx)
        config['tracker']['frames']['ref'] = int(idx)

    @pyqtSlot(result=QVariant)
    def get_bg_frame_idx(self):
        return self.bg_frame_idx

    @pyqtSlot(QVariant)
    def set_n_bg_frames(self, n):
        self.n_bg_frames = int(n)
        config['tracker']['sd_mode']['n_bg_frames']= int(n)

    @pyqtSlot(result=QVariant)
    def get_n_bg_frames(self):
        return self.n_bg_frames

    @pyqtSlot(QVariant)
    def set_start_frame_idx(self, idx):
        self.start_frame_idx = int(idx)
        config['tracker']['frames']['start'] = int(idx)

    @pyqtSlot(result=QVariant)
    def get_start_frame_idx(self):
        return self.start_frame_idx

    @pyqtSlot(QVariant)
    def set_end_frame_idx(self, idx):
        idx = int(idx)
        if idx > 0:
            if idx <= self.start_frame_idx:
                idx = self.start_frame_idx + self.n_bg_frames
        else:
            idx = -1
        self.end_frame_idx = idx
        config['tracker']['frames']['end'] = idx

    @pyqtSlot(result=QVariant)
    def get_end_frame_idx(self):
        return self.end_frame_idx

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
