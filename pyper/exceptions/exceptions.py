
class PyperError(Exception):
    pass


class PyperGUIError(PyperError):
    pass


class PyperValueError(PyperError):
    pass


class PyperNotImplementedError(PyperError, NotImplementedError):
    def __init__(self, msg, arg=None):
        super(PyperNotImplementedError, self).__init__()
        self.msg = msg.format(arg)

    def __str__(self):
        return self.msg


class PyperKeyError(PyperError):
    pass


class PyperRuntimeError(PyperError):

    def __str__(self):
        return "Error import RPi.GPIO, check that module is installed with aptitudeinstall " \
               "python-rpi.gpio or python3-rpi.gpio Also, make sure that you are root"


class CameraCalibrationException(PyperError):
    """
    A Camera calibration specific exception meant to be raised
    if some type problem occurs during calibration
    """
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
