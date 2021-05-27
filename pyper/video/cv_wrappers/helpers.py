import os
import tempfile

from pyper.video.cv_wrappers.video_capture import VideoCapture, VideoCaptureOpenError, VideoCaptureGrabError
from pyper.video.cv_wrappers.video_writer import VideoWriter, VideoWriterOpenError

extensions = (
    'avi',
    'mp4',
    'mpg',
    'h264',
    'ogv',
    'wmv'
)

codecs = (
    'MPG4',
    'X264',
    'THEO',
    'DIVX',
    'WMV2',
    'XVID'
)


# TODO: add version for video_capture
def list_valid_writer_codecs():
    valid_codecs = []
    tmp_folder = tempfile.mkdtemp()
    for container in extensions:
        for codec_str in codecs:
            path = os.path.join(tmp_folder, 'pyper_video_test.{}'.format(container))
            try:
                w = VideoWriter(path, codec_str, 30, (640, 480))
                valid_codecs.append((container, codec_str))
            except VideoWriterOpenError:
                pass
    return valid_codecs


def camera_available(cam_idx=0):
    detected = False
    try:
        cap = VideoCapture(cam_idx)
        try:
            cap.grab()
            detected = True
        except VideoCaptureGrabError:
            detected = False
        finally:
            cap.release()
    except VideoCaptureOpenError:
        detected = False
    return detected
