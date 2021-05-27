from time import sleep

try:
    from pykinect2 import PyKinectV2, PyKinectRuntime
    KINECT_AVAILABLE = True
except ImportError:
    print("pykinect2 not available. Kinect camera will be disabled")
    KINECT_AVAILABLE = False

from pyper.exceptions.exceptions import PyperError
from pyper.video.cv_wrappers.video_capture import VideoCaptureGrabError


class KinectException(PyperError):
    pass


class KinectCam(object):
    def __init__(self):
        self._verbose = False
        self._kinect = None
        self.max_fps = 15
        self.initialize_kinect()

    def initialize_kinect(self):
        self._kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Depth |
            PyKinectV2.FrameSourceTypes_Color)
        sleep(2)  # Allow the kinect to establish com

    def get_shape(self):
        width = self._kinect.color_frame_desc.Width
        height = self._kinect.color_frame_desc.Height
        return width, height

    def read(self):
        if self._kinect.has_new_color_frame():
            frame = self._kinect.get_last_color_frame()
            if frame is not None:
                width, height = self.get_shape()
                frame = frame.reshape(height, width, depth=-1)
            return frame
        else:
            raise VideoCaptureGrabError("No new colour frame available")

    def close(self):
        self._kinect.close()
