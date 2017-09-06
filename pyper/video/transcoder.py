"""
*********************
The transcoder module
*********************

This module is supplied as a utility to convert between openCV video formats to open videos with different players
This may be required if your player doesn't support your format or to fix some videos if some metadata are missing in the file

:author: crousse
"""

import numpy as np
from scipy.misc import imresize
import cv2
from cv2 import cv

from PyQt5.QtCore import QObject, pyqtSlot, QVariant

from pyper.gui.tabs_interfaces import PlayerInterface
from video_stream import RecordedVideoStream

from progressbar import Percentage, Bar, ProgressBar

# TODO: extract format from file extension
# TODO: crop to ROI
# TODO: transcode only between start and endframe


class TranscoderIface(PlayerInterface):
    def __init__(self, app, context, parent, params, display_name, provider_name, timer_speed=20):
        PlayerInterface.__init__(self, app, context, parent, params, display_name, provider_name, timer_speed)
        self.start_frame_idx = 0
        self.end_frame_idx = -1

        self.tracker = None
        self.rois = {'restriction': None}
        self.roi_params = {'restriction': None}

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

    @pyqtSlot()
    def load(self):
        pass

    def load(self):
        """
        Load the video and create the GuiTracker object (or subclass)
        Also registers the analysis image providers (for the analysis tab) with QT
        """
        try:
            self.tracker = Tracker(self, src_file_path=self.params.src_path, dest_file_path=None,
                                   n_background_frames=1, plot=True,
                                   fast=True, camera_calibration=self.params.calib,
                                   callback=None)
        except VideoStreamIOException:
            self.tracker = None
            error_screen = self.win.findChild(QObject, 'videoLoadingErrorScreen')
            error_screen.setProperty('doFlash', True)
            return
        self.stream = self.tracker  # To comply with BaseInterface
        self.tracker.roi = self.rois['tracking']

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
            self.tracker.track_from = self.start_frame_idx
            self.tracker.track_to = self.end_frame_idx if (self.params.end_frame_idx > 0) else None

            if self.rois['restriction'] is not None:
                self.tracker.set_tracking_region_roi(self.rois['restriction'])
            else:
                if self.roi_params['restriction'] is not None:
                    self.tracker.set_tracking_region_roi(self.__get_roi(*self.roi_params['restriction']))


class Transcoder(RecordedVideoStream):
    """
    The transcoder class.
    
    It will convert the video to mp4v (destFilePath should match this extension) but this can be changed easily.
    You can also crop and scale the video at the same time.
    """
    def __init__(self, src_file_path, dest_file_path, bg_start, n_background_frames, crop_params, scale_params):
        RecordedVideoStream.__init__(self, src_file_path, bg_start, n_background_frames)
        self.crop_params = np.array(crop_params)
        self.scale_params = np.array(scale_params)
        size = self.get_final_size()
        self.video_writer = cv2.VideoWriter(dest_file_path,
                                            cv.CV_FOURCC(*'mp4v'),  # FIXME: Format as argument
                                            self.fps,
                                            size[::-1],
                                            True)
        # FIXME: add roi
        # FIXME: add reader
    
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
        widgets = ['Encoding Progress: ', Percentage(), Bar()]  # FIXME: only if CLI (put option in __init__
        pbar = ProgressBar(widgets=widgets, maxval=self.n_frames).start()
        for i in range(self.n_frames):
            pbar.update(i)
            frame = self.read()
            frame = frame[crop_params[0][0]: -crop_params[0][1], crop_params[1][0]: -crop_params[1][1]]
            scale = np.concatenate((self.scale_params, np.array([1]))) * frame.shape
            frame = imresize(frame, scale.astype(int), interp='bilinear')
            self.video_writer.write(frame)
#            self.video_writer.write(np.uint8(np.dstack([frame]*3)))
        pbar.finish()
        self.video_writer.release()
        self.video_writer = None

    def set_tracking_region_roi(self, roi):
        self.tracking_region_roi = roi

    def read(self):
        """
        The required method to behave as a video stream
        It calls self.track() and increments the current_frame_idx
        It also updates the uiIface positions accordingly
        """
        try:
            self.current_frame_idx = self._stream.current_frame_idx + 1
            img = self.transcode_frame(record=self.record, requested_output=self.ui_iface.output_type)
        except EOFError:
            self.ui_iface._stop('End of recording reached')
            # FIXME: stop recording ?
            return
        except cv2.error as e:
            self.ui_iface.timer.stop()
            self._stream.stop_recording('Error {} stopped recording'.format(e))
            return
        return img
