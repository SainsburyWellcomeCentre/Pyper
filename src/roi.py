# -*- coding: utf-8 -*-
"""
**************
The roi module
**************

This module is used to check the position of the mouse relative to an roi

:author: crousse
"""

import numpy as np
from math import radians, cos, sin
import cv2
from cv2 import norm

class Roi(object):
    """
    A generic roi object meant to be subclassed by specific roi shapes.
    It is used to obtain information about points relative to itself.
    """
    def __init__(self):
        pass
    
    def pointInRoi(self, point):
        """
        Returns True if the point is in the roi
        
        :param tuple point: and (x,y) point
        """
        return cv2.pointPolygonTest(self.points, point, False) > 0
        
    def distFromBorder(self, point):
        """
        Returns the distance from the point to the border of the roi
        
        :param tuple point: The (x, y) point to check
        """
        return cv2.pointPolygonTest(self.points, point, True)
        
    def distFromCenter(self, point):
        """
        Returns the distance from the point to the center of mass of the roi
        
        :param tuple point: The (x, y) point to check
        """
        return norm(self.center, point)
        

class Circle(Roi):
    """
    A circle Object that contains an array of points distributed
    on its periphery
    
    Use as follows:
    
    >>> roi = Circle((256, 256), 30) # creates a circle of radius 30 at center 256, 256
    >>> mousePosition = (250, 242)
    >>> if roi.pointInRoi(mousePosition):
    >>>     print('The mouse entered the ROI')
    """

    def __init__(self, center, radius):
        """
        Initialises a circle at center and with given radius
        
        :param tuple center: The center of the circle
        :param int radius: the radius in pixels
        """
        Roi.__init__(self)
        self.center = center
        self.radius = radius
        points = self.getPoints().astype(np.int32)
        self.points = np.expand_dims(points, axis=1)
        
    def circlePoint(self, angle):
        """
        Gets a point on the circle at the given angle
        
        :param angle: the angle in radians
        """
        center = self.center
        radius = self.radius
        x = center[0] + radius * cos(angle)
        y = center[1] + radius * sin(angle)
        return x, y

    def getPoints(self):
        """
        Get 360 points evenly spread on the circle
        
        :return: The list of points.
        :rtype: np.array
        """
        nPoints = 360
        points = np.empty((nPoints, 2), dtype=np.float32)
        for i in range(nPoints):
            points[i] = self.circlePoint(radians(i))
        return points
