import numpy as np
from progressbar import Percentage, Bar, ProgressBar

from pyper.exceptions.exceptions import VideoStreamFrameException
from pyper.tracking.tracking import IS_PI
from pyper.video.video_stream import PiVideoStream, UsbVideoStream, RecordedVideoStream


class Viewer(object):
    """
    A viewer class, a form of simplified Tracker for display purposes
    It can be used to retrieve some parameters of the video or just display
    """
    def __init__(self, src_file_path=None, bg_start=0, n_background_frames=1, delay=5):
        """
        :param str src_file_path: The source file path to read from (camera if None)
        :param int bg_start: The frame to use as first background frame
        :param int n_background_frames: The number of frames to use for the background\
        A number >1 means average
        :param int delay: The time in ms to wait between frames
        """
        track_range_params = (bg_start, n_background_frames)
        if src_file_path is None:
            if IS_PI:
                self._stream = PiVideoStream(dest_file_path, *track_range_params)
            else:
                self._stream = UsbVideoStream(dest_file_path, *track_range_params)
        else:
            self._stream = RecordedVideoStream(src_file_path, *track_range_params)
        self.delay = delay

    def view(self):
        """
        Displays the recording to the user and allows assignment of background frames, tracking start and end
        The user can stop by pressing 'q'

        :return int bg_frame: set using the 'b' key
        :return int track_start: set using the 's' key
        :return int track_end: set using the 'q' key
        """
        is_recording = hasattr(self._stream, 'n_frames')
        if is_recording:
            widgets = ['Video Progress: ', Percentage(), Bar()]
            pbar = ProgressBar(widgets=widgets, maxval=self._stream.n_frames).start()
        bg_frame, track_start, track_end = [None] * 3
        while True:
            try:
                frame = self._stream.read()
                frame_id = self._stream.current_frame_idx
                if frame.shape[2] == 1:
                    frame = np.dstack([frame]*3)
                if not frame.dtype == np.uint8:
                    frame = frame.astype(np.uint8)
                frame = frame.copy()
                kbd_code = frame.display(win_name='Frame',
                                         text='Frame: {}'.format(frame_id),
                                         delay=self.delay,
                                         get_code=True)
                kbd_code = kbd_code if kbd_code == -1 else chr(kbd_code & 255)
                if kbd_code == 'b': bg_frame = frame_id
                elif kbd_code == 's': track_start = frame_id
                elif kbd_code == 'e': track_end = frame_id
                elif kbd_code == 'q':
                    break

                if (bg_frame is not None) and (track_start is not None) and (track_end is not None):
                    break
                if is_recording: pbar.update(frame_id)
            except VideoStreamFrameException: pass
            except (KeyboardInterrupt, EOFError) as e:
                if is_recording: pbar.finish()
                msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
                self._stream.stop_recording(msg)
                break
        if track_end is None:
            track_end = self._stream.current_frame_idx
        if bg_frame is None:
            bg_frame = 0
        if __debug__:
            print(bg_frame, track_start, track_end)
        return bg_frame, track_start, track_end

    def time_str_to_frame_idx(self, time_str):
        """
        Returns the frame number that corresponds to that time.

        :param str time_str: A string of the form 'mm:ss'
        :return Idx: The corresponding frame index
        :rtype: int
        """
        return self._stream.time_str_to_frame_idx(time_str)