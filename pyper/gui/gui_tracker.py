import cv2

from pyper.tracking.tracking import Tracker


class GuiTracker(Tracker):
    """
    A subclass of Tracker that reimplements trackFrame for use with the GUI
    This class implements read() to behave as a stream
    """
    def __init__(self, ui_iface, src_file_path=None, dest_file_path=None,
                 threshold=20, min_area=100, max_area=5000,
                 teleportation_threshold=10,
                 bg_start=0, track_from=1, track_to=None,
                 n_background_frames=1, n_sds=5.0,
                 clear_borders=False, normalise=False,
                 plot=False, fast=False, extract_arena=False,
                 camera_calibration=None,
                 callback=None):
        """
        :param TrackerInterface ui_iface: the interface this tracker is called from

        For the other parameters, see Tracker
        """
        Tracker.__init__(self, src_file_path=src_file_path, dest_file_path=dest_file_path,
                         threshold=threshold, min_area=min_area, max_area=max_area,
                         teleportation_threshold=teleportation_threshold,
                         bg_start=bg_start, track_from=track_from, track_to=track_to,
                         n_background_frames=n_background_frames, n_sds=n_sds,
                         clear_borders=clear_borders, normalise=normalise,
                         plot=plot, fast=fast, extract_arena=extract_arena,
                         camera_calibration=camera_calibration,
                         callback=callback)
        self.ui_iface = ui_iface
        self.record = dest_file_path is not None

    def read(self):
        """
        The required method to behave as a video stream
        It calls self.track() and increments the current_frame_idx
        It also updates the uiIface positions accordingly
        """
        try:
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

    def _plot(self):
        self.paint(self.silhouette, 'c')
        self.silhouette.paint(curve=self.results.positions)