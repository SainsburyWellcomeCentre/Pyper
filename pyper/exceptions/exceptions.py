
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
