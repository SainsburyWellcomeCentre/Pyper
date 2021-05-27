# -*- coding: utf-8 -*-
"""
*************************
The object_contour module
*************************

This module only hosts the ObjectContour class
This class makes it easier to extract contour features and draw them


:author: crousseau
"""

import numpy as np

import cv2
from cv2 import ellipse as cv2_ellipse
from cv2 import fitEllipse, drawContours, moments

from pyper.utilities.utils import colors

OPENCV_VERSION = int(cv2.__version__[0])  # Move to utils or video

DEFAULT_POSITION = (-1, -1)


def diagonal_to_rectangle_points(top_left_pt, bottom_right_pt):
    top_right_pt = (top_left_pt[0], bottom_right_pt[1])
    bottom_left_pt = (bottom_right_pt[0], top_left_pt[1])
    return np.array((top_left_pt, top_right_pt, bottom_right_pt, bottom_left_pt), dtype=np.int32)


class ObjectContour(object):
    """ A contour object to easily extract features from objects and draw """
    def __init__(self, contour, frame=None, contour_type='ellipse', color='w', line_thickness=1):
        """
        :param contour: The contour to make an ObjectContour
        :type contour: array of shape [nPoints, 1, 2]
        :param np.array frame: The frame to draw the contour onto
        :param str contour_type: The type to fit the contour (ellipse or raw) (not fit performed fot raw.
        :param str color: The color to draw the contour. One of 'w', 'r', 'g', 'b', 'y', 'm', 'c'.
        :param int line_thickness: The thickness in pixels of the line to draw the contour
        """
        self.contour = contour
        self.frame = frame
        self.contour_type = contour_type
        self.color = colors[color]
        self.line_thickness = line_thickness
        self._fit()

    def set_params(self, frame, contour_type=None, color=None, line_thickness=None):
        """
        Method to allow the creation a posteriori

        :param np.array frame:
        :param str contour_type:
        :param str color:
        :param int line_thickness:
        :return:
        """
        self.frame = frame
        if contour_type is not None:
            self.contour_type = contour_type
        if color is not None:
            self.color = colors[color]
        if line_thickness is not None:
            self.line_thickness = line_thickness
        self._fit()

    @property
    def area(self):
        return cv2.contourArea(self.contour)

    @staticmethod
    def is_closed_contour(cnt):
        return len(cnt) >= 4

    @property
    def x(self):
        return self.centre[0]

    @property
    def y(self):
        return self.centre[1]
        
    def _fit(self):
        """
        Finds the centre of the object and potentially other parameters based on type
        
        :raise NotImplementedError: if self.contourType not supported
        """
        if self.contour_type == 'ellipse':
            if len(self.contour) >= 5:
                self.fit = fitEllipse(self.contour)
            else:
                self.fit = cv2.minEnclosingCircle(self.contour)
            self.centre = self.fit[0]
            # self.angle = np.round(self.ellipse[2], 1)
            # self.width, self.height = tuple(np.round(self.ellipse[1], 1))
        elif self.contour_type == 'circle':
            self.fit = cv2.minEnclosingCircle(self.contour)
            self.centre = self.fit[0]
        elif self.contour_type == 'rectangle':
            self.fit = cv2.boundingRect(self.contour)
            x, y, width, height = self.fit
            self.centre = (x + width / 2), (y + height / 2)
        elif self.contour_type == 'raw':
            self.fit = moments(self.contour.astype(np.float32))  # FIXME: should not have to convert on the fly
            try:
                x = self.fit['m10'] / self.fit['m00']
                y = self.fit['m01'] / self.fit['m00']
                self.centre = (x, y)
            except ZeroDivisionError:
                self.centre = DEFAULT_POSITION
        else:
            raise NotImplementedError("The show function does not currently"
                                      " support {} contour type".format(self.contour_type))
        
    def draw(self):
        """
        Draws the roi on self.frame with self.color and self.thickness if frame is not None
        
        :raise: NotImplementedError if self.contourType not supported
        """
        if self.frame is None:
            if __debug__:
                print('Frame empty skipping drawing')
            return
        if self.contour_type == 'ellipse':
            cv2_ellipse(self.frame, self.fit, color=self.color, thickness=self.line_thickness)
        elif self.contour_type == 'raw':
            drawContours(self.frame, [self.contour], 0, self.color, self.line_thickness)
        elif self.contour_type == 'rectangle':
            x, y, width, height = self.fit
            cv2.rectangle(self.frame, (x, y), (x+width, y+height), color=self.color, thickness=self.line_thickness)
        else:
            raise NotImplementedError("The show function\
            does not currently support {} contour types".format(self.contour_type))

    def write_coordinates_to_file(self, path, frame_idx):
        """
        Writes parameters to file following:
        'frameNum', 'centreX', 'centreY', 'width', 'height', 'angle'
        
        :param str path: The destination path
        :param int frame_idx: The frame number corresponding to the contour
        """
        with open(path, 'a') as out_file:
            out_file.write('{}\t'.format(frame_idx))
            out_file.write('{}\t{}\t'.format(*self.centre))


class MultiContour(object):
    def __init__(self, contours=None):
        if contours is None:
            contours = []
        self.contours = self.__make_object_contours(contours)

    def __make_object_contours(self, contours):
        _cnts = []
        for cnt in contours:
            if not isinstance(cnt, ObjectContour):
                _cnts.append(ObjectContour(cnt))
            else:
                _cnts.append(cnt)
        return _cnts

    def __bool__(self):
        return len(self) != 0

    __nonzero__ = __bool__  # For python 2

    def __getitem__(self, item):
        return self.contours[item]

    def __len__(self):
        return len(self.contours)

    def append(self, cnt):
        if not isinstance(cnt, ObjectContour):
            cnt = ObjectContour(cnt)
        self.contours.append(cnt)

    @property
    def centres(self):
        return [cnt.centre for cnt in self.contours]

    @property
    def areas(self):
        return [cnt.area for cnt in self.contours]

    def set_params(self, frame, contour_type=None, color=None, line_thickness=None):
        for cnt in self.contours:
            cnt.set_params(frame, contour_type, color, line_thickness)

    def draw(self, line_thickness=1):
        for cnt in self.contours:
            cnt.line_thickness = line_thickness
            cnt.draw()  # OPTIMISE: see if can do in batch
