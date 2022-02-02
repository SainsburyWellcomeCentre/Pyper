import os.path
import tempfile

import cv2
import numpy as np

from pyper.tracking.tracking import Tracker
from pyper.video.video_frame import update_img


class GuiPreviewer(Tracker):
    """
    A subclass of Tracker that reimplements trackFrame for use with the GUI
    This class implements read() to behave as a stream
    The plot method is optimised to be run on a fraction of the frames for speed.
    This is set in the config by curve_update_period.
    """
    def __init__(self, ui_iface, params, src_file_path=None, dest_file_path=None,
                 camera_calibration=None, requested_fps=None):
        """
        :param TrackerInterface ui_iface: The parent Qml interface (from the tabs_interfaces module)

        For the other parameters, see Tracker
        """
        if dest_file_path is None:
            dest_file_path = os.path.join(tempfile.gettempdir(), 'pyper_preview_video.mp4')
        Tracker.__init__(self, params, src_file_path=src_file_path, dest_file_path=dest_file_path,
                         camera_calibration=camera_calibration, requested_fps=requested_fps)
        self.ui_iface = ui_iface
        self.record = dest_file_path is not None
        self.plt_curve = None
        self.seekable = False

    def read(self):
        """
        The required method to behave as a video stream
        It calls self.track() and increments the current_frame_idx
        It also updates the uiIface positions accordingly
        """
        try:
            self.current_frame_idx = self._stream.current_frame_idx + 1
            img = self._stream.read().astype(np.uint8)
        except EOFError:
            self.current_frame = None
            self.ui_iface._stop('End of recording reached')
            return
        except cv2.error as e:
            self.current_frame = None
            self.ui_iface.timer.stop()
            self._stream.stop_recording('Error {} stopped recording'.format(e))
            return
        if img is not None:
            self.current_frame = update_img(self.current_frame, img)
            return img

    @property
    def is_update_frame(self):
        return self.current_frame_idx % self.params.curve_update_period == 0

    @property
    def should_update_vid(self):
        """Ensures not all frames are displayed to save computing power (fast_fast)"""
        should_update = self.is_update_frame or (not self.params.fast)
        return should_update
