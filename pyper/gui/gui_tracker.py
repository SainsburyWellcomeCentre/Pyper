import cv2
import numpy as np  # required for dynamic subclassing

from pyper.tracking.tracking import Tracker


class GuiTracker(Tracker):
    """
    A subclass of Tracker that reimplements trackFrame for use with the GUI
    This class implements read() to behave as a stream
    """
    def __init__(self, ui_iface, params, src_file_path=None, dest_file_path=None,
                 plot=False,  camera_calibration=None,
                 callback=None, requested_fps=None):
        """
        :param TrackerInterface ui_iface: The parent Qml interface (from the tabs_interfaces module)

        For the other parameters, see Tracker
        """
        Tracker.__init__(self, params, src_file_path=src_file_path, dest_file_path=dest_file_path,
                         plot=plot, camera_calibration=camera_calibration,
                         callback=callback, requested_fps=requested_fps)
        self.ui_iface = ui_iface
        self.record = dest_file_path is not None
        self.plt_curve = None

    def read(self):
        """
        The required method to behave as a video stream
        It calls self.track() and increments the current_frame_idx
        It also updates the uiIface positions accordingly
        """
        try:
            if self._stream.seekable:  # Jump to tracking start frame if possible
                if self._stream.current_frame_idx == self._stream.bg_end_frame:
                    self._stream.seek(self.params.start_frame_idx)  # TODO: see if all params updated (including results)

            self.current_frame_idx = self._stream.current_frame_idx + 1
            result = self.track_frame(record=self.record, requested_output=self.ui_iface.output_type)
            self.current_frame = None
        except EOFError:
            self.ui_iface._stop('End of recording reached')
            return
        except cv2.error as e:
            self.ui_iface.timer.stop()
            self._stream.stop_recording('Error {} stopped recording'.format(e))
            return
        if result is not None:
            img, position, distances = result
            self.current_frame = img
            return img

    def _plot(self):  # FIXME: document that not for each frame
        self.paint(self.silhouette, 'c')
        if self.plt_curve is None or self.is_update_frame() or (not self.params.fast):  # do only every x pnts in fast mode
            self.plt_curve = self.results.plot_positions()
        self.silhouette.paint(curve=self.plt_curve)

    def is_update_frame(self):
        return self.current_frame_idx % self.params.curve_update_period == 0

    def should_update_vid(self):  # FIXME: document that not for each frame, + put as fast_fast
        return self.is_update_frame() or (not self.params.fast)

