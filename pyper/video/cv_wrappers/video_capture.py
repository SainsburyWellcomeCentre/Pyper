import cv2

from pyper.exceptions.exceptions import PyperError
from pyper.utilities.utils import un_file
from pyper.video.cv_wrappers.props import CV_PROP_IDS

IS_CV_3 = int(cv2.__version__.split('.')[0]) >= 3


class VideoCaptureGrabError(PyperError):
    pass


class VideoCapturePropertySetError(PyperError):
    pass


class VideoCaptureOpenError(PyperError):
    pass


def try_int(nb):
    try:
        return int(nb)
    except ValueError:
        return False


class VideoCapture(object):
    """
    TODO: See if we could use RGB instead of OpenCV BGR and translate
    TODO: See if we could invert dimensions to make feel native
    """

    def __init__(self, filename_or_cam_idx):
        """

        :param str/int filename_or_cam_idx: Filename to load or index of camera to open
        """
        self.cam_idx = None
        self.filename = None
        self.current_frame_idx = 0
        cam_idx = try_int(filename_or_cam_idx)
        if cam_idx is not False:
            self.cam_idx = cam_idx
            self.capture = cv2.VideoCapture(cam_idx)
        else:
            filename_or_cam_idx = str(filename_or_cam_idx)
            filename_or_cam_idx = un_file(filename_or_cam_idx)
            try:
                open(filename_or_cam_idx, 'r')
            except IOError as err:
                raise VideoCaptureOpenError("Could not open file {} for reading; {}".format(filename_or_cam_idx, err))
            self.filename = filename_or_cam_idx
            self.capture = cv2.VideoCapture(self.filename)

    def reset(self):
        self.set("POS_FRAMES", 0)
        self.current_frame_idx = 0

    def open(self):
        if self.filename is not None:
            self.capture.open(self.filename)
            if not self.is_opened():
                raise VideoCaptureOpenError("Could not open file {} for reading, CODEC may not be supported"
                                            .format(self.filename))
        else:
            self.capture.open(self.cam_idx)
            if not self.is_opened():
                raise VideoCaptureOpenError("Could not open camera number {} for reading".format(self.cam_idx))

    def is_opened(self):
        return self.capture.isOpened()

    def release(self):
        self.capture.release()

    def grab(self):
        has_grabed = self.capture.grab()
        if not has_grabed:
            raise VideoCaptureGrabError("Could not get frame at index {}".format(self.current_frame_idx))

    def retrieve(self):
        has_grabed, img = self.capture.retrieve()
        if not has_grabed:
            raise VideoCaptureGrabError("Could not get frame at index {}".format(self.current_frame_idx))
        self.current_frame_idx += 1
        return img

    def read(self):
        has_grabed, img = self.capture.read()
        if not has_grabed:
            raise VideoCaptureGrabError("Could not get frame at index {}".format(self.current_frame_idx))
        self.current_frame_idx += 1
        return img

    @property
    def frame_width(self):
        return int(self.get('frame_width'))

    @frame_width.setter
    def frame_width(self, width):
        self.set('frame_width', width)

    @property
    def frame_height(self):
        return int(self.get('frame_height'))

    @frame_height.setter
    def frame_height(self, height):
        self.set('frame_height', height)

    @property
    def fps(self):
        return self.get('fps')

    @property
    def n_frames(self):
        return self.get('frame_count')  # TODO: add check for n_frames < 0

    @property
    def fourcc(self):
        return int(self.get('fourcc'))

    @property
    def codec(self):
        """Synonym to fourcc"""
        return int(self.get('fourcc'))

    @property
    def seekable(self):  # FIXME: make cached property or attribute for speed + may not work for acquisition
        return self.n_frames >= 1

    def seek(self, frame_id):
        if self.seekable and 0 <= frame_id < self.n_frames:
            self.set('pos_frames', frame_id)

    def get_prop_id(self, propid):  # TODO: add exception handling for non existing properties (bad spelling)
        if try_int(propid) is not False:
            return try_int(propid)
        else:
            prop_name = "CV_CAP_PROP_{}".format(propid.upper())
            if IS_CV_3:
                propid = CV_PROP_IDS[prop_name]
            else:
                propid = getattr(cv2.cv, prop_name)
            return propid
            
    def get(self, propid):
        propid = self.get_prop_id(propid)
        return self.capture.get(propid)

    def set(self, propid, value):
        """
        It will accept either numerical cv prop ids (enum) or
        property ids that are string with just the property name (e.g. frame_height) and fetch them from cv

        :param propid:
        :param value:
        :return:
        """
        propid = self.get_prop_id(propid)
        has_set = self.capture.set(propid, value)
        if not has_set:
            raise VideoCapturePropertySetError("Could not set property {} to {}"
                                               .format(VideoCapture.get_cv_attribute_name(propid), value))

    @staticmethod
    def get_cv_attributes():
        if IS_CV_3:
            return CV_PROP_IDS.keys()
        else:
            return [attr for attr in dir(cv2.cv) if attr.startswith('CV_CAP_PROP')]

    @staticmethod
    def get_cv_attribute_name(propid):
        for attr in VideoCapture.get_cv_attributes():
            if IS_CV_3:
                if CV_PROP_IDS[attr] == propid:
                    return attr
            else:
                if getattr(cv2.cv, attr) == propid:
                    return attr
