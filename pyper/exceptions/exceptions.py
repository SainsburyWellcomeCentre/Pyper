
class PyperError(Exception):
    pass


class PyperGUIError(PyperError):
    pass


class CameraCalibrationException(PyperError):
    """
    A Camera calibration specific exception meant to be raised
    if some type problem occurs during calibration
    """
    pass


class PyperValueError(PyperError):
    pass


class VideoStreamException(PyperError):
    pass


class VideoStreamFrameException(VideoStreamException):
    """
    A VideoStream specific exception meant to be raised
    if some recoverable frame error occurs
    (e.g. Skipped frame)
    """
    pass


class VideoStreamIOException(VideoStreamException):
    """
    A VideoStream specific exception meant to be raised
    if some i/o problem occurs with the stream
    (e.g. bad cam or unreadable video)
    """
    pass


class VideoStreamTypeException(VideoStreamException):
    """
    A VideoStream specific exception meant to be raised
    if some type problem occurs with the stream
    (e.g. bad input format)
    Especially useful to check since openCV error messages
    not specific
    """
    pass