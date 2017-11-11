# -*- coding: utf-8 -*-
"""
**************
The roi module
**************

This module is used to check the position of the mouse relative to a region of interest (ROI)

:author: crousse
"""
import csv
import numpy as np
from math import radians, cos, sin, sqrt
import cv2
from cv2 import norm, moments


class Roi(object):
    """
    A generic ROI object meant to be sub-classed by specific ROI shapes.
    It is used to obtain information about points relative to itself.
    """
    def __init__(self):
        pass
    
    def contains_point(self, point):
        """
        Returns True if the point is in the ROI
        
        :param tuple point: the (x, y) point to check
        """
        return cv2.pointPolygonTest(self.points, point, False) > 0

    def contains_contour(self, contour):
        for p in contour:
            if not self.contains_point(tuple(p[0])):  # at least one point outside self
                return False
        return True
        
    def dist_from_border(self, point):
        """
        Returns the distance from the point to the border of the ROI
        
        :param tuple point: the (x, y) point to check
        """
        return cv2.pointPolygonTest(self.points, point, True)
        
    def dist_from_center(self, point):
        """
        Returns the distance from the point to the center of mass of the ROI
        
        :param tuple point: the (x, y) point to check
        """
        return norm(self.center, point)

    def to_mask(self, frame):
        mask = frame.copy()  # TODO: extract to roi.to_mask
        mask.fill(0)
        cv2.drawContours(mask, [self.points], 0, 255, cv2.cv.CV_FILLED)
        return mask

    def save(self, dest):  # FIXME: deal with image size
        t = str(type(self)).strip("'<>").split('.')[-1].lower()
        with open(dest, 'w') as out_file:
            out_file.write("{}\n".format(t))
            out_file.write("{}\n".format(self.centre[0]))
            out_file.write("{}\n".format(self.centre[1]))
            out_file.write("{}\n".format(self.width))
            out_file.write("{}\n".format(self.height))
            for pnt in self.points.squeeze():
                out_file.write("{}, {}\n".format(*pnt))  # TODO: format

    @staticmethod
    def load(src_path):
        with open(src_path, 'r') as in_file:
            lines = in_file.readlines()
        return lines

    def get_data(self):
        t = str(type(self)).strip("'<>").split('.')[-1].lower()
        # Uses string to have same interface as save
        roi_data = [t, str(self.centre[0]), str(self.centre[1]), str(self.width), str(self.height)]
        for pnt in self.points.squeeze():
            roi_data.append('{}, {}'.format(*pnt))
        return roi_data


class Circle(Roi):
    """
    A circle Object that contains an array of points distributed on its perimeter
    
    Use as follows:
    
    >>> roi = Circle((256, 256), 30) # creates a circle of radius 30 at center 256, 256
    >>> mouse_position = (250, 242)
    >>> if roi.contains_point(mouse_position):
    >>>     print('The mouse entered the ROI')
    """

    def __init__(self, center, radius):
        """
        Initialises a circle
        
        :param tuple center: the center of the circle
        :param int radius: the radius in pixels
        """
        Roi.__init__(self)
        self.center = center
        self.radius = radius
        points = self.get_points().astype(np.int32)
        self.points = np.expand_dims(points, axis=1)
        
    def circle_point(self, angle):
        """
        Gets a point on the circle at the given angle
        
        :param angle: the angle in radians
        """
        center = self.center
        radius = self.radius
        x = center[0] + radius * cos(angle)
        y = center[1] + radius * sin(angle)
        return x, y

    def get_points(self):
        """
        Get 360 points evenly spaced around the circle perimeter
        
        :return np.array points: the list of points.
        """
        n_points = 360
        points = np.empty((n_points, 2), dtype=np.float32)
        for i in range(n_points):
            points[i] = self.circle_point(radians(i))
        return points


class Rectangle(Roi):

    def __init__(self, top_left_x, top_left_y, width, height):
        Roi.__init__(self)
        self.top_left_point = (top_left_x, top_left_y)
        self.width = width
        self.height = height
        self.center = (int(top_left_x + (width / 2)), int(top_left_y + (height / 2)))
        points = self.get_points().astype(np.int32)
        self.points = np.expand_dims(points, axis=1)

    def get_points(self):
        n_points = 4  # the 4 corners
        points = np.empty((n_points, 2), dtype=np.float32)
        top_x, top_y = self.top_left_point
        points[0] = self.top_left_point
        points[1] = (top_x + self.width, top_y)  # FIXME: use point type instead
        points[2] = (top_x + self.width, top_y + self.height)
        points[3] = (top_x, top_y + self.height)
        return points


class Ellipse(Roi):
    def __init__(self, centre_x, centre_y, width, height):
        Roi.__init__(self)
        self.centre = (centre_x, centre_y)
        self.width = width
        self.height = height
        points = self.get_points().astype(np.int32)
        self.points = np.expand_dims(points, axis=1)

    def __compute_ellipse(self, semi_major, semi_minor, xs):
        return np.array([(semi_major / semi_minor) * sqrt(semi_minor**2 - x**2) for x in xs])

    def get_points(self):
        n_points = 200
        semi_minor = self.height / 2.
        semi_major = self.width / 2.
        xs = np.linspace(-semi_major, semi_major, n_points/2.)  # FIXME: inverted ?
        ys = self.__compute_ellipse(semi_minor, semi_major, xs)   # FIXME: inverted ?
        ys = np.hstack((ys, -ys[::-1])) + self.centre[1]
        xs = np.hstack((xs, xs[::-1])) + self.centre[0]
        points = np.array(zip(xs, ys), dtype=np.float32)
        return points


class FreehandRoi(Roi):
    def __init__(self, points):
        Roi.__init__(self)
        points = np.array(points, dtype=np.int32)
        self.points = np.expand_dims(points, axis=1)
        self.__bounding_rect = cv2.boundingRect(self.points)
        self.width, self.height = self.get_width_height()
        self.centre = self.get_centre()

    def get_width_height(self):
        return self.__bounding_rect[2], self.__bounding_rect[3]

    def get_centre(self):
        return self.__bounding_rect[:2]

