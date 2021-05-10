import cv2
import numpy as np

from pyper.contours.object_contour import ObjectContour, OPENCV_VERSION, MultiContour


class ContoursManager(object):
    """
    Behaves like a list of contours with extra methods
    """
    def __init__(self, contours, n_contours_max=-1):
        self.contours = contours  # FIXME: use ObjectContour objects instead
        self.n_contours_max = n_contours_max
        self.already_sorted = False
        self.not_in_range = False  # Some contours found but not the right size

    # def __getattr__(self, method):
    #     return getattr(self.contours, method)

    def __len__(self):
        return len(self.contours)

    def __getitem__(self, item):
        return self.contours[item]

    def get_areas(self):
        return [cv2.contourArea(cnt) for cnt in self.sorted()]  # TODO: check if should be ObjectContour type

    def get_biggest_area(self):
        cnts = self.sorted()
        if cnts:
            return cv2.contourArea(cnts[0])  # TODO: check if should be ObjectContour type
        else:
            return

    def update(self, mask):
        self.not_in_range = False
        self.contours = ContoursManager._extract_contours(mask)
        self.already_sorted = False

    def to_mask(self, shape):
        return np.array(cv2.drawContours(np.zeros(shape), self.contours, -1, (255, 255, 255), cv2.FILLED),
                        dtype='uint8')

    def sort(self, decreasing=True):
        if not self.already_sorted:
            self.contours = self.sorted(decreasing)
        self.already_sorted = True

    def sorted(self, decreasing=True):
        if self.already_sorted:
            return self.contours
        else:
            return sorted(self.contours, key=cv2.contourArea, reverse=decreasing)

    def get_biggest(self, check_in_roi=None):
        for cnt in self.sorted():
            if ObjectContour.is_closed_contour(cnt) and (check_in_roi is None or check_in_roi.contains_contour(cnt)):
                return ObjectContour(cnt)
        return None  # all contours have failed

    def get_in_range(self, min_area, max_area, n_contours_max=None, check_in_roi=None):
        if n_contours_max is None:
            n_contours_max = self.n_contours_max
        out = MultiContour()
        self.not_in_range = False  # Some contours found but not the right size
        for cnt in self.sorted():
            area = cv2.contourArea(cnt)
            if area < min_area:  # contours are getting too small
                if len(out) == 0:
                    self.not_in_range = True
                return out
            elif area > max_area:
                self.not_in_range = True
                continue
            else:
                if check_in_roi is None or check_in_roi.contains_contour(cnt):
                    out.append(cnt)
                    self.not_in_range = False
                    if len(out) == n_contours_max:
                        break
        return out

    @classmethod
    def from_mask(cls, mask):  # OPTIMISE: compare perfs of CHAIN_APPROX_SIMPLE and CHAIN_APPROX_NONE
        """
        Get the list of contours in the mask sorted by decreasing size

        :param np.array mask: The mask to extract the contours from
        :return: The reverse sorted list of contours
        """
        contours = cls._extract_contours(mask)
        if contours:
            return cls(contours)

    @staticmethod
    def _extract_contours(mask):
        cnt_export_mode = cv2.RETR_EXTERNAL
        cnt_approx_method = cv2.CHAIN_APPROX_SIMPLE
        try:
            if OPENCV_VERSION == 2:
                contours, _ = cv2.findContours(np.copy(mask), mode=cnt_export_mode,
                                               method=cnt_approx_method)  # OPTIMISE: check if copy necessary
            elif OPENCV_VERSION == 3:
                _, contours, _ = cv2.findContours(np.copy(mask), mode=cnt_export_mode, method=cnt_approx_method)
        except ValueError:
            contours = cv2.findContours(np.copy(mask), mode=cnt_export_mode, method=cnt_approx_method)
        return contours
