import os
import sys
from skimage.io import imread

from PyQt5.QtCore import QObject, pyqtSlot, Qt, QVariant, pyqtSignal, pyqtProperty
from PyQt5.QtWidgets import QFileDialog

from pyper.config.parameters import Parameters
from pyper.config.conf import config
from pyper.gui.tabs_interfaces import STRUCTURE_TRACKER_CLASSES, VIDEO_FILTERS, VIDEO_FORMATS
from pyper.utilities.utils import un_file
from pyper.video.kinect_cam import KINECT_AVAILABLE


class AdvancedThresholdingParameters(object):
    def __init__(self):
        self.is_enabled = False
        self.min_threshold = config['tracker']['advanced_thresholding']['min_threshold'].copy()
        self.max_threshold = config['tracker']['advanced_thresholding']['max_threshold'].copy()
        self.min_area = config['tracker']['detection']['min_area']
        self.max_area = config['tracker']['detection']['max_area']
        self.n_structures_max = config['tracker']['detection']['n_structures_max']  # Default number of structures  # FIXME: set graphically
        self.tracker_class = STRUCTURE_TRACKER_CLASSES['default']


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
        self.structure_tracker_classes = STRUCTURE_TRACKER_CLASSES
        self.tracker_class = self.structure_tracker_classes["default"]  # TODO: remove

        self._curve_update_period = self.config['gui']['update_period']

        self.ref = None
        self.fast = False
        self.plot = False

        self.current_object = ''
        self.structures = {}

    def __del__(self):
        """
        Reset the standard out on destruction
        """
        sys.stdout = sys.__stdout__

    @pyqtSlot(str)
    def set_object_name(self, obj_name):
        if obj_name in self.structures.keys():
            self.current_object = obj_name
        else:
            raise ValueError('Unknown object "{}"'.format(obj_name))

    @pyqtSlot(str)
    def set_advanced_thresholding(self, structure_name):
        if structure_name not in self.structures.keys():
            self.structures[structure_name] = AdvancedThresholdingParameters()

    @pyqtSlot(str, str)
    def rename_structure(self, old_name, new_name):
        if old_name in self.structures.keys():
            self.structures[new_name] = self.structures.pop(old_name)
            if self.current_object == old_name:
                self.current_object = new_name

    @pyqtSlot(str)
    def remove_structure(self, structure_name):
        if structure_name in self.structures.keys():
            self.structures.pop(structure_name)

    curve_update_period_signal = pyqtSignal()
    @pyqtProperty(int, notify=curve_update_period_signal)
    def curve_update_period(self):
        return self._curve_update_period

    @curve_update_period.setter
    def curve_update_period(self, period):
        self._curve_update_period = period
        self.config['gui']['update_period'] = period

    @pyqtSlot(str, str)
    def set_thresholding_type(self, structure_name, thresholding_type):
        thresholding_type = thresholding_type.lower()
        if thresholding_type in self.structure_tracker_classes.keys():
            self.set_tracker_type(thresholding_type, structure_name)
        else:
            raise NotImplementedError("Unknown thresholding method {}".format(thresholding_type))

    @pyqtSlot()
    def write_defaults(self):
        """
        Writes defaults to the config file
        """
        self.config.write()

    @pyqtSlot(str)
    def set_tracker_type(self, tracker_type, structure_name=''):
        try:
            if isinstance(tracker_type, str):
                tracker_class = self.structure_tracker_classes[tracker_type]
            else:
                tracker_class = tracker_type
        except KeyError:
            print("Type must be one of {}, got: {}".format(self.structure_tracker_classes.keys(), tracker_type))
            return

        if structure_name:
            self.structures[structure_name].tracker_class = tracker_class
        else:
            self.tracker_class = tracker_class

    @pyqtSlot(str)
    def chg_cursor(self, cursor_type='cross'):
        if cursor_type == 'cross':
            self.app.setOverrideCursor(Qt.CursorShape(Qt.CrossCursor))
        elif cursor_type == 'point_hand':
            self.app.setOverrideCursor(Qt.CursorShape(Qt.PointingHandCursor))
        else:
            raise NotImplementedError('Unknown cursor type {}'.format(cursor_type))

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
        """ The QT dialog to select the path to save the recorded video """
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

    # ADVANCED THRESHOLDING
    @pyqtSlot(str, int, int)
    def set_min_threshold(self, struct_name, idx, value):
        struct_name = struct_name if struct_name else self.current_object
        self.structures[struct_name].min_threshold[idx] = value

    @pyqtSlot(str, result=QVariant)
    def get_min_threshold(self, struct_name=''):
        struct_name = struct_name if struct_name else self.current_object
        return self.structures[struct_name].min_threshold

    @pyqtSlot(str, int, int)
    def set_max_threshold(self, struct_name, idx, value):
        self.structures[struct_name].max_threshold[idx] = value

    @pyqtSlot(str, result=QVariant)
    def get_max_threshold(self, struct_name=''):
        struct_name = struct_name if struct_name else self.current_object
        max_thrsh = self.structures[struct_name].max_threshold
        return max_thrsh

    @pyqtSlot(str, result=int)
    def get_min_area(self, struct_name=''):  # WARNING: resembles property of simple version
        struct_name = struct_name if struct_name else self.current_object
        return self.structures[struct_name].min_area

    @pyqtSlot(str, int)
    def set_min_area(self, struct_name, area):
        self.structures[struct_name].min_area = area

    @pyqtSlot(str, result=int)
    def get_max_area(self, struct_name=''):  # WARNING: resembles property of simple version
        struct_name = struct_name if struct_name else self.current_object
        return self.structures[struct_name].max_area

    @pyqtSlot(str, int)
    def set_max_area(self, struct_name, area):
        self.structures[struct_name].max_area = area

    @pyqtSlot(str, result=int)
    def get_n_structures_max(self, struct_name):
        return self.structures[struct_name].n_structures_max

    @pyqtSlot(str, int)
    def set_n_structures_max(self, struct_name, n):
        self.structures[struct_name].n_structures_max = n

    @pyqtSlot(str, QVariant)
    def register_structure_ctrl(self, struct_name, ctrl):
        self.structures[struct_name].control = ctrl

    @pyqtSlot(int, int)
    def set_current_threshold(self, idx, color_value):  # FIXME: hacky
        if "min" in self.current_threshold_object_name.lower():
            self.set_min_threshold(self.current_object, idx, color_value)
        elif "max" in self.current_threshold_object_name.lower():
            self.set_max_threshold(self.current_object, idx, color_value)

    @pyqtSlot(str, bool, str)
    def set_picking_colour(self, struct_name, is_picking, threshold_object_name):  # required here to link the 2 windows
        if threshold_object_name:  # FIXME: hacky
            self.current_threshold_object_name = threshold_object_name
        if struct_name:
            self.current_object = struct_name
        self.is_picking_colour = is_picking  # TODO: check if used
        colour_picking = self.win.findChild(QObject, "trackerColourPicking")
        colour_picking.setProperty('enabled', is_picking)
        if not is_picking:
            self.restore_cursor()
            ctrl = self.structures[self.current_object].control
            threshold_ctrl = ctrl.findChild(QObject, self.current_threshold_object_name)
            if "min" in self.current_threshold_object_name.lower():
                threshold_ctrl.set_value(*self.structures[self.current_object].min_threshold)  # FIXME: hacky
            elif "max" in self.current_threshold_object_name.lower():
                threshold_ctrl.set_value(*self.structures[self.current_object].max_threshold)

    @pyqtSlot(str, bool)
    def set_enabled(self, struct_name, enabled):
        self.structures[struct_name].is_enabled = enabled

    @pyqtSlot(result=bool)
    def kinect_cam_available(self):
        return KINECT_AVAILABLE
