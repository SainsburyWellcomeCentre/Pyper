# -*- coding: utf-8 -*-
"""
*************************
The gui_interfaces module
*************************

Creates the class links to allow the graphical interface.
It essentially implements a class for each graphical interface tab.

:author: crousse
"""

import os
import re
import uuid
from time import time

import matplotlib
import numpy as np
from scipy.io import loadmat
from skimage.io import imsave

from pyper.analysis.video_analysis import VideoAnalyser
from pyper.gui.gui_tracker import GuiTracker

matplotlib.use('qt5agg')  # For OSX otherwise, the default backend doesn't allow to draw to buffer
from matplotlib import pyplot as plt

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, pyqtSlot, QVariant, QTimer

from pyper.utilities.utils import qurl_to_str, un_file
from pyper.video.video_stream import RecordedVideoStream, QuickRecordedVideoStream, ImageListVideoStream
from pyper.tracking.structure_tracker import ColorStructureTracker, StructureTrackerGui, HsvStructureTracker
from pyper.contours.roi import Rectangle, Ellipse, FreehandRoi, Roi, RoiCollection
from pyper.camera.camera_calibration import CameraCalibration
from pyper.gui.image_providers import CvImageProvider
from pyper.video.cv_wrappers import helpers as cv_helpers
from pyper.analysis import video_analysis

from pyper.exceptions.exceptions import VideoStreamIOException, PyperError
from pyper.config import conf
config = conf.config

VIDEO_FILTERS = "Videos (*.avi *.h264 *.mpg *.mp4)"
VIDEO_FORMATS = ('.avi', '.h264', '.mpg', '.mp4')

STRUCTURE_TRACKER_CLASSES = {
    'default': StructureTrackerGui,
    'b&w': StructureTrackerGui,
    'hsv': HsvStructureTracker,
    'rgb': ColorStructureTracker,  # OPTIMISE: split based on colour order
    'bgr': ColorStructureTracker
        # FIXME: add pupil structuretracker PupilGuiTracker
}


class BaseInterface(QObject):
    """
    Abstract interface
    This class is meant to be sub-classed by the other classes of the module
    PlayerInterface, TrackerIface (base themselves to ViewerIface, CalibrationIface, RecorderIface)
    It supplies the base methods and attributes to register an object with video in qml.
    It also possesses an instance of ParamsIface to 
    """
    def __init__(self, app, context, parent, params, display_name, provider_name, timer_speed=20):
        """

        :param QApplication app:
        :param QQmlContext context:
        :param QObject parent:
        :param pyper.gui.gui_parameters.GuiParameters params:
        :param str display_name:
        :param str provider_name:
        :param int timer_speed: interval in ms for the timer
        """
        QObject.__init__(self, parent)
        self.app = app  # necessary to avoid QPixmap bug: must construct a QGuiApplication before
        self.ctx = context
        self.win = parent
        self.display_name = display_name
        self.provider_name = provider_name
        self.params = params

        self.stream = None
        self.n_frames = 0
        
        self.timer = QTimer(self)
        self.timer_speed = params.timer_period
        self.timer.timeout.connect(self.get_img)

    def get_img(self):
        """The method called by self.timer to play the video"""
        if -1 <= self.stream.current_frame_idx < self.n_frames:
            try:
                self.display.reload()
                self._update_display_idx()
            except EOFError:
                self.timer.stop()
        else:
            self.timer.stop()

    def _set_display(self):
        """
        Gets the display from the qml code
        """
        self.display = self.win.findChild(QObject, self.display_name)

    def _update_display_idx(self):
        """
        Updates the value of the display progress bar
        """
        self.display.setProperty('value', self.stream.current_frame_idx)
        
    def _set_display_max(self):
        """
        Sets the maximum of the display progress bar
        """
        self.display.setProperty('maximumValue', self.n_frames)
    
    @pyqtSlot(result=QVariant)
    def get_frame_idx(self):
        """
        pyQT slot to return the index of the currently displayed frame
        """
        return str(self.stream.current_frame_idx)
        
    @pyqtSlot(result=QVariant)
    def get_n_frames(self):
        """
        pyQT slot to return the number of frames of the current display
        """
        return self.n_frames

    def clip_end_frame_idx(self):
        if self.params.end_frame_idx in (0, -1):
            self.params.end_frame_idx = self.n_frames
        
    def _update_img_provider(self):
        """
        Registers the objects image provider with the qml code
        Based on self.provider_name
        """
        engine = self.ctx.engine()
        self.image_provider = CvImageProvider(requestedImType='pixmap', stream=self.stream)
        engine.addImageProvider(self.provider_name, self.image_provider)

    @pyqtSlot(int, int, int, int, result=QVariant)
    def get_pixel_colour(self, img_width, img_height, pixel_x, pixel_y):
        src_height, src_width = self.image_provider.img.shape[:2]  # OpenCV coordinates
        pixel_x *= src_width / img_width
        pixel_x = round(pixel_x)
        pixel_y *= src_height / img_height
        pixel_y = round(pixel_y)
        # pixel = self.image_provider.img[pixel_x-5: pixel_x+5, pixel_y-5:pixel_y+5, :]
        # colour = [int(v) for v in pixel.mean(axis=(0, 1))]
        pixel = self.image_provider.img[pixel_y, pixel_x, :]
        colour = [int(v) for v in pixel]  # QML only understands pure python
        return colour

    @pyqtSlot(str, result=bool)
    def load_graph_data(self, graph_obj_name):
        """
        Load a 1 dimensional vector to display alongside the tracking.
        If the sampling is not the same, it should be a multiple of the video frame rate.
        """
        diag = QFileDialog()
        src_path = diag.getOpenFileName(parent=diag,
                                        caption='Choose data file',
                                        directory=os.getenv('HOME'),
                                        filter="Data (*.mat *.npy *.csv)",
                                        initialFilter="Data (*.npy)")

        src_path = src_path[0]
        if src_path:
            extension = os.path.splitext(src_path)[-1]
            if extension == '.npy':
                self.graph_data = np.load(src_path)
            elif extension == '.mat':
                self.graph_data = loadmat(src_path)  # TEST:
            elif extension == '.csv':
                self.graph_data = np.genfromtext(src_path, delimiter=',')  # TEST:
            else:
                raise PyperError("Unknown extension: {}".format(extension))
            graph_object = self.win.findChild(QObject, graph_obj_name)
            data_str = ";".join([str(d) for d in self.graph_data])
            graph_object.setProperty("points", data_str)
            return True
        else:
            return False
        # FIXME: add resampling to fit video length


class PlayerInterface(BaseInterface):
    """
    This (abstract) class extends the BaseInterface to allow controllable videos (play, pause, forward...)
    """
    @pyqtSlot()
    def play(self):
        """
        Start video (timer) playback
        """
        self.timer_speed = self.params.timer_period
        self.timer.start(self.timer_speed)

    @pyqtSlot()
    def pause(self):
        """
        Pause video (timer) playback
        """
        self.timer.stop()

    @pyqtSlot(QVariant)
    def move(self, step_size):
        """
        Moves in the video by stepSize
        
        :param int step_size: The number of frames to scroll by (positive or negative)
        """
        target_frame = self.stream.current_frame_idx
        target_frame -= 1  # reset
        target_frame += int(step_size)
        self.seek_to(target_frame)

    @pyqtSlot(QVariant)
    def seek_to(self, frame_idx):
        """
        Seeks directly to frameIdx in the video
        
        :param int frame_idx: The frame to get to
        """
        self.stream.current_frame_idx = self._validate_frame_idx(frame_idx)
        if self.stream.seekable:
            self.stream.seek(frame_idx)
        self.get_img()
    
    def _validate_frame_idx(self, frame_idx):
        """
        Checks if the supplied frameIdx is within [0:n_frames]

        :returns: A bound index
        :rtype: int
        """
        if frame_idx >= self.n_frames:
            frame_idx = self.n_frames - 1
        elif frame_idx < 0:
            frame_idx = 0
        return frame_idx


class ViewerIface(PlayerInterface):
    """
    Implements the PlayerInterface class with a RecordedVideoStream or QuickRecordedVideoStream
    It is meant for video preview with frame precision seek
    """

    @pyqtSlot()
    def load(self):
        """
        Loads the video into memory
        """
        try:
            recorded_stream = RecordedVideoStream(self.params.src_path, 0, 1)
            self.seekable = recorded_stream.stream.seekable  # FIXME: add to init
            if self.seekable:
                self.stream = recorded_stream
            else:  # Wee need a low definition of video to mimic seeking
                print('Video is not seekable, creating low resolution video for browsing')
                self.stream = QuickRecordedVideoStream(self.params.src_path, 0, 1)
        except VideoStreamIOException:
            self.stream = None
            error_screen = self.win.findChild(QObject, 'viewerVideoLoadingErrorScreen')
            error_screen.setProperty('doFlash', True)
            return
        self.n_frames = self.stream.n_frames - 1

        self._set_display()
        self._set_display_max()
        self._update_img_provider()

    @pyqtSlot(str)  # FIXME: make inherited by all but calib ?
    def save_ref_source(self, dest_path):
        dest_path = un_file(dest_path)
        self.stream.seek(self.stream.current_frame_idx - 1)
        frame = self.stream.read()
        imsave(dest_path, frame)


class CalibrationIface(PlayerInterface):
    """
    Implements the PlayerInterface class with an ImageListVideoStream
    It uses the CameraCalibration class to compute the camera matrix from a set of images containing a
    chessboard pattern.
    """
    def __init__(self, app, context, parent, params, display_name, provider_name, timer_speed=20):
        PlayerInterface.__init__(self, app, context, parent, params, display_name, provider_name, timer_speed)
        
        self.n_columns = config['calibration']['n_columns']
        self.n_rows = config['calibration']['n_rows']
        self.calib = CameraCalibration(self.n_columns, self.n_rows)
        self.matrix_type = 'normal'

        self.src_folder = ""
        
        self._set_display()
        self._set_display()  # TODO check why 2

    @pyqtSlot()
    def calibrate(self):
        """
        Compute the camera matrix 
        """
        self.calib = CameraCalibration(self.n_columns, self.n_rows)
        self.calib.calibrate(self.src_folder)
        self.params.calib = self.calib
        
        self.n_frames = len(self.calib.src_imgs)
        
        self.stream = ImageListVideoStream(self.calib.src_imgs)
        self._set_display()
        self._set_display_max()
        
        self._update_img_provider()

    @pyqtSlot(result=QVariant)
    def get_n_rows(self):
        """
        Get the number of inner rows in the chessboard pattern
        """
        return self.n_rows

    @pyqtSlot(QVariant)
    def set_n_rows(self, n_rows):
        """Set the number of inner rows in the chessboard pattern"""
        self.n_rows = int(n_rows)

    @pyqtSlot(result=QVariant)
    def get_n_columns(self):
        """Get the number of inner columns in the chessboard pattern"""
        return self.n_columns

    @pyqtSlot(QVariant)
    def set_n_columns(self, n_columns):
        """Set the number of inner rows in the chessboard pattern"""
        self.n_columns = int(n_columns)

    @pyqtSlot(result=QVariant)
    def get_folder_path(self):
        """Get the path to the folder where the images with the pattern are stored"""
        diag = QFileDialog()
        src_folder = diag.getExistingDirectory(parent=diag, caption="Chose directory", directory=os.getenv('HOME'))
        self.src_folder = src_folder
        return src_folder

    @pyqtSlot(QVariant)
    def set_matrix_type(self, matrix_type):
        """
        Set the matrix type to be saved. Resolution independent (normal) or dependant (optimized)
        
        :param string matrix_type: The type of matrix to be saved. One of ['normal', 'optimized']
        """
        matrix_type = matrix_type.lower()
        if matrix_type not in ['normal', 'optimized']:
            raise KeyError("Expected one of ['normal', 'optimized'], got {}".format(matrix_type))
        else:
            self.matrix_type = matrix_type

    @pyqtSlot()
    def save_camera_matrix(self):
        """
        Save the camera matrix selected as self.matrixType
        """
        diag = QFileDialog()
        dest_path = diag.getSaveFileName(parent=diag,
                                         caption='Save matrix',
                                         directory=os.getenv('HOME'),
                                         filter='Numpy (.npy)')
        dest_path = dest_path[0]
        if dest_path:
            if self.matrix_type == 'normal':
                np.save(dest_path, self.camera_matrix)
            elif self.matrix_type == 'optimized':
                np.save(dest_path, self.optimal_camera_matrix)

    @pyqtSlot(QVariant)
    def set_frame_type(self, frame_type):
        """
        Selects the type of frame to be displayed. (Before, during or after distortion correction)
        
        :param string frame_type: The selected frame type. One of ['source', 'detected', 'corrected']
        """
        frame_type = frame_type.lower()
        current_index = self.stream.current_frame_idx
        frame_types = {"source": self.calib.src_imgs,
                       "detected": self.calib.detected_imgs,
                       "corrected": self.calib.corrected_imgs}
        try:
            imgs = frame_types[frame_type]
        except KeyError:
            raise KeyError("Expected one of ['source', 'detected', 'corrected'], got {}".format(frame_type))
        self.stream = ImageListVideoStream(imgs)
        self._update_img_provider()
        self.stream.current_frame_idx = self._validate_frame_idx(current_index - 1)  # reset to previous position
        self.get_img()


class TrackerIface(BaseInterface):
    """
    This class implements the BaseInterface to provide a qml interface
    to the GuiTracker (or subclass thereof) object of the tracking module.
    """
    def __init__(self, app, context, parent, params, display_name, provider_name,
                 analysis_provider_1, analysis_provider_2):
        BaseInterface.__init__(self, app, context, parent, params, display_name, provider_name)

        self.tracker = None
        self.video_analyser = None

        self.rois = {'tracking': None,  # FIXME: multiple (f(structure)
                     'restriction': None,
                     'measurement': None}
        self.roi_params = {k: None for k in self.rois.keys()}
        self.rois_vault = {k: {} for k in self.rois.keys()}  # FIXME: inner is ordered dict

        self.analysis_image_provider = analysis_provider_1
        self.analysis_image_provider2 = analysis_provider_2

        self.graph_data = None

        self.current_frame_idx = 0
        self.output_type = "Raw"

        self.start_track_time = None
        self.end_track_time = None

    @pyqtSlot()
    def prevent_video_update(self):
        if hasattr(self, 'image_provider'):
            self.image_provider.reuse_on_next_load = True

    @pyqtSlot(int, result=QVariant)
    def get_row(self, idx):
        """
        Get the data (position ... from the TrackingResults object) at row idx
        
        :param int idx: The index of the row to return
        """
        if self.video_analyser is None:
            print("No tracker instance, make sure you have selected the correct result type")
            return -1

        if self.video_analyser.row_in_range(idx):
            row = self.video_analyser.get_row(idx)
            if row:
                return row
            else:
                return -1
        else:
            return -1

    @pyqtSlot(str)
    def save_ref_source(self, dest_path):
        if self.stream.current_frame is not None:
            dest_path = un_file(dest_path)
            imsave(dest_path, self.stream.current_frame)

    @pyqtSlot()
    def load(self):
        """
        Load the video and create the GuiTracker object (or subclass)
        Also registers the analysis image providers (for the analysis tab) with QT
        """
        self.params.fast = True
        self.params.plot = True
        try:
            self.params.n_background_frames = 1
            self.tracker = GuiTracker(self, self.params, src_file_path=self.params.src_path,
                                      dest_file_path=None, camera_calibration=self.params.calib)
        except VideoStreamIOException:
            self.tracker = None
            error_screen = self.win.findChild(QObject, 'videoLoadingErrorScreen')
            error_screen.setProperty('doFlash', True)
            return
        self.stream = self.tracker  # To comply with BaseInterface
        self.tracker.roi = self.rois['tracking']

        self.n_frames = self.tracker._stream.n_frames - 1
        self.current_frame_idx = self.tracker._stream.current_frame_idx

        self.clip_end_frame_idx()

        self.video_analyser = VideoAnalyser(self.tracker, self.get_sampling_freq())
        
        self._set_display()
        self._set_display_max()
        self._update_img_provider()

    @pyqtSlot(QVariant)
    def save_roi_vault(self, roi_type):
        diag = QFileDialog()
        default_dir = os.getenv('HOME')
        dest_file_path = diag.getSaveFileName(parent=diag,
                                              caption='Choose data file',
                                              directory=default_dir,
                                              filter="Archive (*.tar *.bz2 *.gzip *.zip)",
                                              initialFilter="Archive (*.bz2)")
        dest_file_path = dest_file_path[0]
        vault = RoiCollection(self.rois_vault[roi_type].values())
        vault.compress(dest_file_path)

    @pyqtSlot(QVariant)
    def load_roi_vault(self, roi_type):
        diag = QFileDialog()
        default_dir = os.getenv('HOME')
        src_file_path = diag.getOpenFileName(parent=diag,
                                             caption='Choose data file',
                                             directory=default_dir,
                                             filter="Archive (*.tar *.bz2 *.gzip *.zip)",
                                             initialFilter="Archive (*.bz2)")
        src_file_path = src_file_path[0]
        self.load_roi_vault_from_path(roi_type, src_file_path)

    def load_roi_vault_from_path(self, roi_type, src_file_path):
        vault = RoiCollection()
        vault.decompress(src_file_path)
        self.loaded_uuids = []
        for roi in vault:
            _uuid = self.get_uuid()
            self.rois_vault[roi_type][_uuid] = roi
            self.loaded_uuids.append(_uuid)

    @pyqtSlot(QVariant, result=QVariant)
    def retrieve_next(self, roi_type):
        try:
            _uuid = self.loaded_uuids.pop()
        except IndexError:
            return -1
        roi = self.rois_vault[roi_type][_uuid]
        self.rois[roi_type] = roi
        roi_data = [_uuid] + list(self.tracker._stream.size) + roi.get_data()
        return roi_data

    @pyqtSlot()
    def set_tracker_params(self):
        if self.tracker is not None:
            self.tracker._stream.bg_start_frame = self.params.bg_frame_idx
            self.tracker._stream.bg_end_frame = self.params.bg_frame_idx + self.params.n_bg_frames - 1
            self.clip_end_frame_idx()
            self.tracker.bg.source = self.params.ref  # TODO: add check for validity of frame size/type in tracker

    def _set_tracker_roi(self, roi_type, tracker_method):
        """

        :param str roi_type:
        :param method tracker_method:
        :return:
        """
        if roi_type not in self.rois.keys():
            return
        if self.rois[roi_type] is not None:
            for idx in range(len(self.tracker.structures)):  # OPTIMISE: improve to set specifically in the future
                tracker_method(self.rois[roi_type], idx)
        else:
            if self.roi_params[roi_type] is not None:
                for idx in range(len(self.tracker.structures)):
                    tracker_method(self._get_roi(*self.roi_params[roi_type]), idx)  # OPTIMISE: improve to set specifically in the future

    @pyqtSlot()
    def set_tracker_rois(self):  # REFACTOR: refactor tracking.Tracker to use roi dictionary and extract method  # FIXME: do for != structures
        if self.tracker is not None:
            # self.tracker.set_rois(self.rois)  # REFACTOR:
            self._set_tracker_roi('tracking', self.tracker.set_roi)
            self._set_tracker_roi('restriction', self.tracker.set_tracking_region_roi)
            self._set_tracker_roi('measurement', self.tracker.set_measure_roi)

    def _reset_measures(self):
        if self.tracker is not None:
            self.tracker.reset_measures()   # reset between runs

    def pre_track(self):
        """
        A method to be overwritten to allow execution of custom code before start in
        derived classes
        """
        self.start_track_time = time()
        # self.timer_speed = int(1 / self.tracker._stream.stream.fps)
        self.tracker.set_start_time(self.start_track_time)

    def post_track(self):
        self.end_track_time = time()
        if self.start_track_time is not None:
            n_frames = self.tracker._stream.current_frame_idx
            duration = float(self.end_track_time - self.start_track_time)
            fps = n_frames / duration
            print("Handled {0} frames in {1:.2f} seconds (fps={2:.2f})".format(n_frames, duration, fps))

    @pyqtSlot()
    def start(self):
        """
        Start the tracking of the loaded video with the parameters from self.params
        """
        if self.tracker is not None:
            self._reset_measures()
            self.set_tracker_params()
            self.set_tracker_rois()
            self.pre_track()
            self.timer_speed = self.params.timer_period
            self.timer.start(self.timer_speed)

    @pyqtSlot()
    def stop(self):
        """
        The qt slot to self._stop()
        """
        self._stop('Recording stopped manually')
        
    def _stop(self, msg):
        """
        Stops the tracking gracefully
        
        :param string msg: The message to print upon stoping
        """
        self.timer.stop()
        self.post_track()
        self.tracker._stream.stop_recording(msg)
        self.image_provider.reuse_on_next_load = True  # Prevents loading on next resize

    def __get_scaling_factors(self, width, height):
        stream_width, stream_height = self.tracker._stream.size  # flipped for openCV
        horizontal_scaling_factor = stream_width / width
        vertical_scaling_factor = stream_height / height
        return horizontal_scaling_factor, vertical_scaling_factor

    def __get_scaled_roi_rectangle(self, source_type, img_width, img_height, roi_x, roi_y, roi_width, roi_height):
        horizontal_scaling_factor, vertical_scaling_factor = self.__get_scaling_factors(img_width, img_height)
        if 'ellipse' in source_type.lower():  # Top left based
            scaled_x = (roi_x + roi_width / 2.) * horizontal_scaling_factor
            scaled_y = (roi_y + roi_height / 2.) * vertical_scaling_factor
        elif 'rectangle' in source_type.lower():  # Center based
            scaled_x = roi_x * horizontal_scaling_factor
            scaled_y = roi_y * vertical_scaling_factor
        else:
            raise NotImplementedError("Unknown ROI shape: {}".format(source_type))  # FIXME: change exception type
        scaled_width = roi_width * horizontal_scaling_factor
        scaled_height = roi_height * vertical_scaling_factor
        return scaled_x, scaled_y, scaled_width, scaled_height

    def __assign_roi(self, roi_type, roi):
        try:
            self.rois[roi_type] = roi
            if roi is None:
                self.roi_params[roi_type] = None
        except KeyError:
            raise NotImplementedError("Unknown ROI type: {}".format(roi_type))

    def _get_roi(self, source_type, img_width, img_height, roi_x, roi_y, roi_width, roi_height):
        scaled_coords = self.__get_scaled_roi_rectangle(source_type, img_width, img_height,
                                                        roi_x, roi_y, roi_width, roi_height)
        if 'rectangle' in source_type.lower():
            roi = Rectangle(*scaled_coords)
        elif 'ellipse' in source_type.lower():
            roi = Ellipse(*scaled_coords)
        else:
            raise NotImplementedError("Unknown ROI shape: {}".format(source_type))
        return roi
        
    @pyqtSlot(str, str, float, float, float, float, float, float)
    def set_roi(self, roi_type, source_type, img_width, img_height, roi_x, roi_y, roi_width, roi_height):  # FIXME: do for != structures
        """
        Sets the ROI (in which to check for the specimen) from the one drawn in QT
        Scaling is applied to match the (resolution difference) between the representation 
        of the frames in the GUI (on which the user draws the ROI) and the internal representation
        used to compute the position of the specimen.

        :param str roi_type: The type of roi, one of ("tracking", "restriction", "measurement")
        :param str source_type: The string representing the source type
        :param float img_width: The width of the image representation in the GUI
        :param float img_height: The height of the image representation in the GUI
        :param float roi_x: The centre of the roi in the first dimension
        :param float roi_y: The centre of the roi in the second dimension
        :param float roi_width: The width of the ROI
        :param float roi_height: The height of the ROI
        """
        source_type = qurl_to_str(source_type)
        if self.tracker is not None:
            roi = self._get_roi(source_type, img_width, img_height, roi_x, roi_y, roi_width, roi_height)
            self.__assign_roi(roi_type, roi)
        else:
            self.roi_params[roi_type] = source_type, img_width, img_height, roi_x, roi_y, roi_width, roi_height
            print("No tracker available, will assign later.")

    def __get_roi_from_points(self, img_width, img_height, points):
        exp = re.compile('\d+')
        points = points.split("),")
        points = np.array([map(float, exp.findall(p)) for p in points], dtype=np.float32)
        horizontal_scaling_factor, vertical_scaling_factor = self.__get_scaling_factors(img_width, img_height)
        points[:, 0] *= horizontal_scaling_factor
        points[:, 1] *= vertical_scaling_factor
        roi = FreehandRoi(points)
        return roi

    @pyqtSlot(str, float, float, QVariant)
    def set_roi_from_points(self, roi_type, img_width, img_height, points):
        if self.tracker is not None:
            roi = self.__get_roi_from_points(img_width, img_height, points)
            self.__assign_roi(roi_type, roi)
        else:
            self.roi_params[roi_type] = img_width, img_height, points

    @pyqtSlot(QVariant)
    def remove_roi(self, roi_type):
        self.__assign_roi(roi_type, None)

    @pyqtSlot(result=QVariant)
    def get_uuid(self):
        return uuid.uuid4().hex[:10]

    @pyqtSlot(QVariant, QVariant)
    def store_roi(self, roi_type, uuid):
        self.rois_vault[roi_type][uuid] = self.rois[roi_type]  # FIXME: check if exists first

    @pyqtSlot(QVariant, QVariant, result=QVariant)
    def retrieve_roi(self, roi_type, uuid):
        roi = self.rois_vault[roi_type][uuid]
        self.rois[roi_type] = roi
        self.set_tracker_rois()
        return list(self.tracker._stream.size) + roi.get_data()

    @pyqtSlot(str)
    def save_roi(self, roi_type):
        diag = QFileDialog()
        default_dest = os.getenv('HOME')
        dest_path = diag.getSaveFileName(parent=diag,
                                         caption='Save file',
                                         directory=default_dest,
                                         filter="ROI (*.roi)")
        dest_path = dest_path[0]
        if dest_path:
            roi = self.rois[roi_type]
            if roi is not None:
                roi.save(dest_path)
            else:
                print("No ROI to save")

    @pyqtSlot(result=QVariant)
    def load_roi(self):
        diag = QFileDialog()
        default_src = os.getenv('HOME')
        src_path = diag.getOpenFileName(parent=diag,
                                        caption='Load file',
                                        directory=default_src,
                                        filter="ROI (*.roi)")
        src_path = src_path[0]
        if src_path:
            return Roi.load(src_path)
        else:
            return -1

    @pyqtSlot(QVariant)
    def save(self, default_dest):
        """
        Save the data (positions and other measures, see tracker.results attributes) as a csv style file
        """
        diag = QFileDialog()
        if default_dest:
            default_dest = os.path.splitext(default_dest)[0] + '.csv'
        else:
            default_dest = os.getenv('HOME')
        dest_path = diag.getSaveFileName(parent=diag,
                                         caption='Save file',
                                         directory=default_dest,
                                         filter="Text (*.txt *.dat *.csv)",
                                         initialFilter="Text (*.csv)")
        dest_path = dest_path[0]
        if dest_path:
            self.tracker.multi_results.to_csv(dest_path)


    @pyqtSlot(QVariant)
    def set_frame_type(self, output_type):
        """
        Set the type of frame to display. (As source, difference with background or binary mask)
        
        :param string output_type: The type of frame to display. One of ['Raw', 'Diff', 'Mask']
        """
        self.output_type = output_type.lower()

    @pyqtSlot()
    def analyse_angles(self):
        """
        Compute and plot the angles between the segment Pn -> Pn+1 and Pn+1 -> Pn+2
        """
        if self.tracker is not None:
            self.analysis_image_provider._fig = self.video_analyser.analyse_angles()

    @pyqtSlot()
    def analyse_distances(self):
        """
        Compute and plot the distances between the points Pn and Pn+1
        """
        if self.tracker is not None:
            self.analysis_image_provider2._fig = self.video_analyser.analyse_distances()

    @pyqtSlot()
    def save_angles_fig(self):
        """
        Save the graph as a png or jpeg image
        """
        if self.tracker is not None:
            self.video_analyser.save_fig(self.analysis_image_provider.get_array())

    def get_sampling_freq(self):
        return self.tracker._stream.fps

    def get_img(self):
        if self.tracker._stream.current_frame_idx < self.n_frames:
            self.display.reload()
            self._update_display_idx()
        else:
            self._stop('End of recording reached')


class RecorderIface(TrackerIface):
    """
    This class extends the TrackerIface to provide video acquisition and live detection (tracking).
    It uses openCV to run the camera and thus should work with any camera supported by openCV.
    It uses the first available USB/firewire camera unless the platform is a raspberry pi,
    in which case it will use the pi camera.
    """

    @pyqtSlot()
    def load(self):
        pass
        
    @pyqtSlot(result=QVariant)
    def start(self):
        """
        Start the recording and tracking.
        
        :returns: The recording was started status code
        """
        if not hasattr(self.params, 'dest_path'):
            return False
        vid_ext = os.path.splitext(self.params.dest_path)[1]
        if vid_ext not in VIDEO_FORMATS:
            print('Unknown format: {}'.format(vid_ext))
            return False

        self._reset_measures()

        self.clip_end_frame_idx()
        self.params.fast = True
        self.params.plot = True

        requested_fps = round(1/(self.params.timer_period / 1000))  # convert period to seconds
        if __debug__:
            print("Timer period: '{}'ms, requested FPS: '{}'Hz".format(self.params.timer_period, requested_fps))

        try:
            self.params.n_background_frames = 1
            self.tracker = GuiTracker(self, self.params, src_file_path=None, dest_file_path=self.params.dest_path,
                                      camera_calibration=self.params.calib, requested_fps=requested_fps)
        except VideoStreamIOException as err:
            self.tracker = None
            print("Error starting capture, ", err.args)
            # error_screen = self.win.findChild(QObject, 'videoLoadingErrorScreen')
            # error_screen.setProperty('doFlash', True)
            return
        self.stream = self.tracker  # To comply with BaseInterface
        self.video_analyser = VideoAnalyser(self.tracker, self.get_sampling_freq())

        self._set_display()
        self._update_img_provider()
        
        self.tracker.set_roi(self.rois['tracking'], 0)  # FIXME:

        self.pre_track()
        period = round((1 / self.tracker._stream.stream.fps) * 1000)
        self.timer_speed = period  # convert to ms
        self.timer.start(self.timer_speed)
        return True
        
    def get_sampling_freq(self):
        """
        Return the sampling frequency (note this is a maximum and can be limited by a slower CPU)
        """
        return 1.0 / (self.timer_speed / 1000.0)  # timer speed in ms

    @pyqtSlot(str)
    def set_camera(self, cam_name):
        if cam_name == "kinect" or cam_name.startswith("usb"):  # TODO: add pi
            self.camera = cam_name


    @pyqtSlot(int, result=QVariant)
    def cam_detected(self, cam_idx):
        """
        Check if a camera is available
        """
        return cv_helpers.camera_available(cam_idx)

    def get_img(self):
        self.display.reload()
