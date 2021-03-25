import os

from skimage.io import imread

from PyQt5.QtCore import pyqtSignal, pyqtProperty

from pyper.config import conf
from pyper.utilities.utils import un_file

config = conf.config


# def dont_decorate(f):
#     """decorator to exclude methods"""
#     f.decorate = False
#     return f
#
#
# setter_decorator = pyqtSlot(QVariant)
#
#
# getter_decorator = pyqtSlot(result=QVariant)
#
#
# def decorate_all():
#     """decorate all instance methods (unless excluded) with the same decorator"""
#     def decorate(cls):
#         methods = inspect.getmembers(cls, inspect.isroutine)
#         accessors = [(m_name, m) for m_name, m in methods if m_name.startswith('get_')]
#         mutators = [(m_name, m) for m_name, m in methods if m_name.startswith('set_')]
#         for attr_name, method in accessors:
#             decorated_method = getter_decorator(method)
#             setattr(cls, attr_name, decorated_method)
#         for attr_name, method in mutators:
#             decorated_method = setter_decorator(method)
#             # print(id(method), id(decorated_method), set(dir(method)) ^ set(dir(decorated_method)))
#             setattr(cls, attr_name, decorated_method)
#         return cls
#     return decorate


class Parameters(object):
    def __init__(self, _config=None):
        if _config is None:
            _config = config
        self.config = _config

        self._bg_frame_idx = self.config['tracker']['frames']['ref']
        self._n_bg_frames = self.config['tracker']['sd_mode']['n_background_frames']
        self._start_frame_idx = self._bg_frame_idx + self._n_bg_frames
        self._end_frame_idx = self.config['tracker']['frames']['end']

        self._detection_threshold = self.config['tracker']['detection']['threshold']
        self._objects_min_area = self.config['tracker']['detection']['min_area']
        self._objects_max_area = self.config['tracker']['detection']['max_area']
        self._teleportation_threshold = self.config['tracker']['detection']['teleportation_threshold']
        self._n_erosions = self.config['tracker']['detection']['n_erosions']

        self._n_sds = self.config['tracker']['sd_mode']['n_sds']

        self._clear_borders = self.config['tracker']['checkboxes']['clear_borders']
        self._normalise = self.config['tracker']['checkboxes']['normalise']
        self._extract_arena = self.config['tracker']['checkboxes']['extract_arena']
        self._infer_location = self.config['tracker']['checkboxes']['infer_location']

        self._timer_period = self.config['global']['timer_period']

    def _set_defaults(self):
        """
        Reset the parameters to default.
        To customise the defaults, users should do this in the config file.
        """
        self._bg_frame_idx = self.config['tracker']['frames']['ref']
        self._n_bg_frames = self.config['tracker']['sd_mode']['n_background_frames']
        self._start_frame_idx = self._bg_frame_idx + self._n_bg_frames
        self._end_frame_idx = self.config['tracker']['frames']['end']

        self._detection_threshold = self.config['tracker']['detection']['threshold']
        self._objects_min_area = self.config['tracker']['detection']['min_area']
        self._objects_max_area = self.config['tracker']['detection']['max_area']
        self._teleportation_threshold = self.config['tracker']['detection']['teleportation_threshold']
        self._n_erosions = self.config['tracker']['detection']['n_erosions']

        self._n_sds = self.config['tracker']['sd_mode']['n_sds']

        self._clear_borders = self.config['tracker']['checkboxes']['clear_borders']
        self._normalise = self.config['tracker']['checkboxes']['normalise']
        self._extract_arena = self.config['tracker']['checkboxes']['extract_arena']
        self._infer_location = self.config['tracker']['checkboxes']['infer_location']

        self._timer_period = self.config['global']['timer_period']

    def write_defaults(self):
        self.config.write()

    timer_period_signal = pyqtSignal()
    @pyqtProperty(int, notify=timer_period_signal)
    def timer_period(self):
        return self._timer_period

    @timer_period.setter
    def timer_period(self, period):
        self._timer_period = period

    # BOOLEAN OPTIONS
    clear_borders_signal = pyqtSignal()
    @pyqtProperty(bool, notify=clear_borders_signal)
    def clear_borders(self):
        return self._clear_borders

    @clear_borders.setter
    def clear_borders(self, status):
        self._clear_borders = status
        self.config['tracker']['checkboxes']['clear_borders'] = status

    normalise_signal = pyqtSignal()
    @pyqtProperty(bool, notify=normalise_signal)
    def normalise(self):
        return self._normalise

    @normalise.setter
    def normalise(self, status):
        self._normalise = status
        self.config['tracker']['checkboxes']['normalise'] = status

    extract_arena_signal = pyqtSignal()
    @pyqtProperty(bool, notify=extract_arena_signal)
    def extract_arena(self):
        return self._extract_arena

    @extract_arena.setter
    def extract_arena(self, status):
        self._extract_arena = status
        self.config['tracker']['checkboxes']['extract_arena'] = status

    infer_location_signal = pyqtSignal()
    @pyqtProperty(bool, notify=infer_location_signal)
    def infer_location(self):
        return self._infer_location

    @infer_location.setter
    def infer_location(self, status):
        self._infer_location = status
        self.config['tracker']['checkboxes']['infer_location'] = status

    # DETECTION OPTIONS
    detection_threshold_signal = pyqtSignal()
    @pyqtProperty(int, notify=detection_threshold_signal)
    def detection_threshold(self):
        return self._detection_threshold

    @detection_threshold.setter
    def detection_threshold(self, threshold):
        self._detection_threshold = threshold
        self.config['tracker']['detection']['threshold'] = threshold

    min_area_signal = pyqtSignal()
    @pyqtProperty(int, notify=min_area_signal)
    def min_area(self):
        return self._objects_min_area

    @min_area.setter
    def min_area(self, area):
        self._objects_min_area = area
        self.config['tracker']['detection']['min_area'] = area

    max_area_signal = pyqtSignal()
    @pyqtProperty(int, notify=max_area_signal)
    def max_area(self):
        return self._objects_max_area

    @max_area.setter
    def max_area(self, area):
        self._objects_max_area = area
        self.config['tracker']['detection']['max_area'] = area

    max_mvmt_signal = pyqtSignal()
    @pyqtProperty(int, notify=max_mvmt_signal)
    def max_movement(self):
        return self._teleportation_threshold

    @max_movement.setter
    def max_movement(self, movement):
        self._teleportation_threshold = movement
        self.config['tracker']['detection']['teleportation_threshold'] = movement

    n_erosions_signal = pyqtSignal()
    @pyqtProperty(int, notify=n_erosions_signal)
    def n_erosions(self):
        return self._n_erosions

    @n_erosions.setter
    def n_erosions(self, n_erosions):
        if n_erosions >= 0:
            self._n_erosions = n_erosions
            self.config['tracker']['detection']['n_erosions'] = n_erosions

    n_sds_signal = pyqtSignal()
    @pyqtProperty(int, notify=n_sds_signal)
    def n_sds(self):
        return self._n_sds

    @n_sds.setter
    def n_sds(self, n_sds):
        self._n_sds = n_sds
        self.config['tracker']['sd_mode']['n_sds'] = n_sds

    # FRAME OPTIONS
    bg_frame_idx_signal = pyqtSignal()
    @pyqtProperty(int, notify=bg_frame_idx_signal)
    def bg_frame_idx(self):
        return self._bg_frame_idx

    @bg_frame_idx.setter
    def bg_frame_idx(self, idx):
        self._bg_frame_idx = idx
        self.config['tracker']['frames']['ref'] = idx

    n_bg_frames_signal = pyqtSignal()
    @pyqtProperty(int, notify=n_bg_frames_signal)
    def n_bg_frames(self):
        return self._n_bg_frames

    @n_bg_frames.setter
    def n_bg_frames(self, n):
        self._n_bg_frames = n
        self.config['tracker']['sd_mode']['n_background_frames'] = n

    start_frame_idx_signal = pyqtSignal()
    @pyqtProperty(int, notify=start_frame_idx_signal)
    def start_frame_idx(self):
        return self._start_frame_idx

    @start_frame_idx.setter
    def start_frame_idx(self, idx):
        self._start_frame_idx = idx
        self.config['tracker']['frames']['start'] = idx

    end_frame_idx_signal = pyqtSignal()
    @pyqtProperty(int, notify=end_frame_idx_signal)
    def end_frame_idx(self):
        return self._end_frame_idx

    @end_frame_idx.setter
    def end_frame_idx(self, idx):
        if idx > 0:
            if idx <= self._start_frame_idx:
                idx = self._start_frame_idx + self._n_bg_frames
        else:
            idx = -1
        self._end_frame_idx = idx
        self.config['tracker']['frames']['end'] = idx

    # PATH OPTIONS
    def get_path(self):
        return self.src_path if self.is_path_selected() else ""

    def get_file_name(self):
        path = self.get_path()
        return os.path.basename(path) if path else ""

    def get_dest_path(self):
        return self.dest_path if hasattr(self, "dest_path") else ""

    def set_ref_source(self, ref_path):
        ref_path = un_file(ref_path)
        self.ref = imread(ref_path)
