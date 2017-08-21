# -*- coding: utf-8 -*-
"""
**************
The roi module
**************

This module is used to check the position of the mouse relative to a region of interest (ROI)

:author: crousse
"""

import numpy as np
from math import radians, cos, sin, sqrt
import cv2
from cv2 import norm


class Roi(object):
    """
    A generic ROI object meant to be sub-classed by specific ROI shapes.
    It is used to obtain information about points relative to itself.
    """
    def __init__(self):
        pass
    
    def point_in_roi(self, point):
        """
        Returns True if the point is in the ROI
        
        :param tuple point: the (x, y) point to check
        """
        return cv2.pointPolygonTest(self.points, point, False) > 0
        
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
        

class Circle(Roi):
    """
    A circle Object that contains an array of points distributed on its perimeter
    
    Use as follows:
    
    >>> roi = Circle((256, 256), 30) # creates a circle of radius 30 at center 256, 256
    >>> mouse_position = (250, 242)
    >>> if roi.point_in_roi(mouse_position):
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



