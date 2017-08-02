# -*- coding: utf-8 -*-
"""
**************
The roi module
**************

This module is used to check the position of the mouse relative to a region of interest (ROI)

:author: crousse
"""

import numpy as np
from math import radians, cos, sin
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
