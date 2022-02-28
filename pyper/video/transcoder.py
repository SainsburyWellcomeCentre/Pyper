"""
*********************
The transcoder module
*********************

This module is supplied as a utility to convert between openCV video formats to open videos with different players
This may be required if your player doesn't support your format or to fix some videos if some metadata are missing in the file

:author: crousse
"""

import os
import math

import numpy as np
from skimage.transform import resize
from tqdm import trange
import cv2

from PyQt5.QtCore import pyqtSlot, QVariant

from pyper.exceptions.exceptions import VideoStreamIOException, PyperValueError
from pyper.gui.gui_tracker import GuiTracker
from pyper.gui.tabs_interfaces import TrackerIface
from pyper.video.cv_wrappers.video_writer import VideoWriter
from pyper.video.video_stream import RecordedVideoStream


# TODO: see if can avoid to swap axis multiple times for Transcoder below

class TranscoderIface(TrackerIface):
    CODECS_TO_EXTS = {".mp4": "MPG4",
                      ".mpg": "MPG4",
                      ".h264": "X264",
                      ".ogv": "THEO",
                      ".avi": "DIVX",
                      ".wmv": "WMV2"
                      # ".h265": "X265",
                      # ".avi": "PIM1"
                      # "xvid"
                      # "MJPG"
                      }
    EXTS_TO_CODECS = {v: k for k, v in CODECS_TO_EXTS.items()}

    def __init__(self, app, context, parent, params, display_name, provider_name):
        TrackerIface.__init__(self, app, context, parent, params, display_name, provider_name, None, None)
        self.start_frame_idx = 0
        self.end_frame_idx = -1
        self.dest_file_path = self.params.dest_path
        self.source_path = self.params.src_path

        self.tracker = None
        self.tracking_region_roi = None  # to comply with TrackerTab interface
        self.rois = {'restriction': None}
        self.roi_params = {'restriction': None}

        self.scale_params = [1, 1]
        self.codec = None

    @pyqtSlot(str)
    def set_codec(self, codec):  # TODO: QML code needs drop down menu with codecs
        if self.dest_file_path:
            extension = os.path.splitext(self.dest_file_path)[-1]
            extension = extension.lower()
            if extension != TranscoderIface.EXTS_TO_CODECS[codec]:
                raise ValueError("Transcoder mismatch between codec '{}' and extension '{}'. Expected {}."
                                 .format(codec, extension, TranscoderIface.EXTS_TO_CODECS[codec]))
            self.codec = codec

    @pyqtSlot(float, float)
    def set_scale(self, x_scale, y_scale):  # TODO: QML code needs menu (float from 0.1 to 1)
        self.scale_params = [x_scale, y_scale]

    @pyqtSlot(float)
    def set_x_scale(self, x_scale):
        self.scale_params[0] = x_scale

    @pyqtSlot(float)
    def set_y_scale(self, y_scale):
        self.scale_params[1] = y_scale

    @pyqtSlot(int)
    def set_start_frame_idx(self, idx):
        self.start_frame_idx = idx

    @pyqtSlot(result=QVariant)
    def get_start_frame_idx(self):
        return self.start_frame_idx

    @pyqtSlot(int)
    def set_end_frame_idx(self, idx):
        self.end_frame_idx = idx

    @pyqtSlot(result=QVariant)
    def get_end_frame_idx(self):
        return self.end_frame_idx

    @pyqtSlot(str)
    def set_save_path(self, dest_path):
        self.dest_file_path = dest_path

    @pyqtSlot(str)
    def set_source_path(self, source_path):
        self.source_path = source_path

    def _infer_codec(self):
        codec_extension = os.path.splitext(self.dest_file_path)[-1]
        codec_extension = codec_extension.lower()
        try:
            codec = TranscoderIface.CODECS_TO_EXTS[codec_extension]
        except KeyError:
            raise PyperValueError("Unknown container: {}, needs to be on of {}".
                                  format(codec_extension, TranscoderIface.CODECS_TO_EXTS.keys()))
        return codec

    @pyqtSlot()
    def load(self):
        """
        Load the video and create the GuiTranscoder object
        """
        if self.codec is None:
            self.codec = self._infer_codec()
        try:
            self.params.n_background_frames = 1
            self.tracker = GuiTranscoder(self, self.params, src_file_path=self.source_path,
                                         dest_file_path=self.dest_file_path,
                                         camera_calibration=self.params.calib, codec=self.codec,
                                         roi=self.rois['restriction'], scale_params=self.scale_params)
        except VideoStreamIOException as err:
            self.tracker = None
            print("Could not create tracker object; {}".format(err))
            # error_screen = self.win.findChild(QObject, 'videoLoadingErrorScreen')
            # error_screen.setProperty('doFlash', True)
            return
        self.stream = self.tracker  # To comply with BaseInterface
        # self.tracker.set_tracking_region_roi(self.rois['restriction'])

        self.n_frames = self.tracker._stream.n_frames - 1
        self.current_frame_idx = self.tracker._stream.current_frame_idx

        if self.params.end_frame_idx == -1:
            self.params.end_frame_idx = self.n_frames

        self._set_display()
        self._set_display_max()
        self._update_img_provider()

    @pyqtSlot()
    def set_tracker_params(self):
        if self.tracker is not None:
            self.params.start_frame_idx = self.start_frame_idx
            if self.end_frame_idx == -1:
                self.params.end_frame_idx = self.tracker._stream.n_frames - 1

            if self.rois['restriction'] is not None:
                self.tracker.set_tracking_region_roi(self.rois['restriction'])
            else:
                if self.roi_params['restriction'] is not None:
                    params = self.roi_params['restriction']
                    self.tracker.set_tracking_region_roi(self._get_roi(*params))


class GuiTranscoder(GuiTracker):
    """
    The transcoder class.
    
    It will convert the video to mp4v (destFilePath should match this extension) but this can be changed easily.
    You can also crop and scale the video at the same time.
    """
    def __init__(self, ui_iface, params, src_file_path, dest_file_path,
                 camera_calibration, roi, scale_params, codec):
        GuiTracker.__init__(self, ui_iface, params, src_file_path=src_file_path, dest_file_path=dest_file_path,
                            camera_calibration=camera_calibration)
        self.codec = [str(c) for c in codec]

        # WARNING: these params needs to be before call to set_tracking_region_roi
        self.scale_params = np.array(scale_params)  # (scale_x, scale_y), e.g. (0.5, 0.75)
        self.dest_file_path = dest_file_path

        if roi is not None:
            self.set_tracking_region_roi(roi)
        else:
            self.tracking_region_roi = None  # To comply w/ interface

        self.crop_params = self._get_crop_params()
        output_size = self._get_final_size()

        self.video_writer = VideoWriter(self.dest_file_path,
                                        self.codec,
                                        float(self._stream.fps),
                                        output_size[::-1],  # invert size with openCV
                                        True)

    def _update_video_writer(self):
        self.crop_params = self._get_crop_params()
        output_size = self._get_final_size()
        self.video_writer = VideoWriter(self.dest_file_path,
                                        self.codec,
                                        float(self._stream.fps),
                                        output_size[::-1],  # invert size with openCV
                                        True)

    def set_tracking_region_roi(self, roi):  # FIXME: signatures does not match parent
        self.tracking_region_roi = roi
        self._update_video_writer()

    def _get_crop_params(self):
        if self.tracking_region_roi is not None:
            roi_width = self.tracking_region_roi.width
            roi_height = self.tracking_region_roi.height
            top_x, top_y = self.tracking_region_roi.top_left_point
            scale_x, scale_y = self.scale_params
            cropped_width = top_x + self._scale_crop_param(roi_width, scale_x)
            cropped_height = top_y + self._scale_crop_param(roi_height, scale_y)
            crop_x = (int(top_x), int(cropped_width))
            crop_y = (int(top_y), int(cropped_height))
            crop_params = (crop_y, crop_x)  # Flipped because of openCV weirdness
        else:
            crop_params = (0, self._stream.height), (0, self._stream.width)  # Flipped because of openCV weirdness
        return crop_params

    def _scale_crop_param(self, crop_param, scale_param):
        """
        Adjust by flooring so that scaling the cropped version will give an integer.

        :param crop_param: The width or height of the cropping before scaling
        :param scale_param: The matching vertical or horizontal scaling factor
        :return: The adjusted width or height
        """
        return int(math.floor(crop_param * scale_param) / scale_param)
    
    def _get_final_size(self):
        crop_x, crop_y = self.crop_params
        cropped_width = crop_x[1] - crop_x[0]
        cropped_height = crop_y[1] - crop_y[0]
        cropped_size = np.array((cropped_width, cropped_height))

        final_size = cropped_size * self.scale_params
        final_size = tuple(final_size.astype(np.uint32))
        return final_size

    def _crop_frame(self, frame):
        crop_x, crop_y = self.crop_params
        cropped_frame = frame[crop_x[0]: crop_x[1], crop_y[0]: crop_y[1]]
        return cropped_frame

    def _scale_frame(self, frame):
        scale = np.concatenate((self.scale_params, np.array([1]))) * frame.shape  # REFACTOR: make more "numpyic"
        scaled_frame = resize(frame, scale.astype(int), preserve_range=True, anti_aliasing=True)
        return scaled_frame
    
    def transcode_frame(self):
        frame = self._stream.read()
        original_frame = frame.copy()
        if self._stream.current_frame_idx >= self.params.end_frame_idx:
            raise EOFError("End of tracking reached")
        if self.params.start_frame_idx <= self._stream.current_frame_idx:
            frame = self._crop_frame(frame)
            frame = self._scale_frame(frame)
            self.video_writer.write(frame.astype(np.uint8))
        return original_frame

    def finalise_recording(self):
        self.video_writer.release()
        self.video_writer = None

    def read(self):
        """
        The required method to behave as a video stream
        It calls self.track() and increments the current_frame_idx
        It also updates the ui_iface positions accordingly
        """
        try:
            self.current_frame_idx = self._stream.current_frame_idx + 1
            img = self.transcode_frame()
        except EOFError:
            self.finalise_recording()  # FIXME: trigger when track_end reached
            self.ui_iface._stop('End of recording reached')
            return
        except cv2.error as e:
            self.ui_iface.timer.stop()
            self._stream.stop_recording('Error {} stopped recording'.format(e))
            return
        return img


class Transcoder(RecordedVideoStream):  # FIXME: does not seem to be used
    """
    The Transcoder class.

    It will convert the video to mp4v (dest_file_path should match this extension) but this can be changed easily.
    You can also crop and scale the video at the same time.
    """

    def __init__(self, src_file_path, dest_file_path, bg_start, n_background_frames, crop_params, scale_params):
        RecordedVideoStream.__init__(self, src_file_path, bg_start, n_background_frames)
        self.crop_params = np.array(crop_params)
        self.scale_params = np.array(scale_params)
        size = self.get_final_size()
        self.video_writer = VideoWriter(dest_file_path,
                                        'mp4v',  # FIXME: Format as argument
                                        self.fps,
                                        size[::-1],
                                        True)

    def get_final_size(self):
        cropped_width = self.size[0] - sum(self.crop_params[0])
        cropped_height = self.size[1] - sum(self.crop_params[1])
        cropped_size = np.array((cropped_width, cropped_height))

        final_size = cropped_size * self.scale_params
        final_size = tuple(final_size.astype(np.uint32))
        return final_size

    def transcode(self):
        crop_params = self.crop_params
        final_width, final_height = self.get_final_size()
        for i in trange(self.n_frames):  # FIXME: progressbar only if CLI (put option in __init__)
            frame = self.read()
            frame = frame[crop_params[0][0]: -crop_params[0][1], crop_params[1][0]: -crop_params[1][1]]
            scale = np.concatenate((self.scale_params, np.array([1]))) * frame.shape
            frame = resize(frame, scale.astype(int), preserve_range=True, anti_aliasing=True)
            self.video_writer.write(frame)
        # self.video_writer.write(np.uint8(np.dstack([frame]*3)))
        self.video_writer.release()
        self.video_writer = None
