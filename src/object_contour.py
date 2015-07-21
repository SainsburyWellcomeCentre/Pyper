# -*- coding: utf-8 -*-
"""
*************************
The object_contour module
*************************

This module only hosts the ObjectContour class
This class makes it easier to extract contour features and draw them


:author: crousse
"""
from cv2 import ellipse as cv2Ellipse
from cv2 import fitEllipse, drawContours, moments

import numpy as np

class ObjectContour(object):
    """ A contour object to easily extract features from objects and draw """
    def __init__(self, contour, frame, contourType='ellipse', color='w', lineThickness=1):
        """
        :param contour: The contour to make an ObjectContour
        :type contour: array of shape [nPoints, 1, 2]
        :param frame: The frame to draw the contour onto
        :type frame: an image
        :param str contourType: The type to fit the contour (ellipse or raw) (not fit performed fot raw.
        :param str color: The color to draw the contour. One of 'w', 'r', 'g', 'b', 'y', 'm'.
        :param int lineThickness: The thickness in pixels of the line to draw the contour
        """
        colors = {'w': (255, 255, 255),
                  'r': (0, 0, 255),
                  'g': (0, 255, 0),
                  'b': (255, 0, 0), 
                  'y': (0, 255, 255),
                  'c': (255, 255, 0),
                  'm': (255, 0, 255)}
        self.contour = contour
        self.frame = frame
        self.contourType = contourType
        self.color = colors[color]
        self.lineThickness = lineThickness
        self._fit()

    @property
    def x(self):
        return self.centre[0]

    @property
    def y(self):
        return self.centre[1]
        
    def _fit(self):
        """
        Finds the center of the object and potentially other parameters based on type
        
        :raise NotImplementedError: if self.contourType not supported
        """
        if self.contourType == 'ellipse':
            self.fit = fitEllipse(self.contour)
            self.centre = self.fit[0]
#           self.angle = np.round(self.ellipse[2], 1)
#           self.width, self.height = tuple(np.round(self.ellipse[1], 1))
        elif self.contourType == 'raw':
            self.fit = moments(self.contour.astype(np.float32)) # FIXME: should not have to convert on the fly
            x = self.fit['m10'] / self.fit['m00']
            y = self.fit['m01'] / self.fit['m00']
            self.centre = (x, y)
        else:
            raise NotImplementedError("The show function\
            does not currently support {} contour types".format(self.contourType))
        
    def draw(self):
        """
        Draws the roi on self.frame with self.color and self.thickness if frame is not None
        
        :raise: NotImplementedError if self.contourType not supported
        """
        if self.frame is None:
            if __debug__:
                print('Frame empty skipping drawing')
            return
        if self.contourType == 'ellipse':
            cv2Ellipse(self.frame, self.fit, color=self.color, thickness=self.lineThickness)
        elif self.contourType == 'raw':
            drawContours(self.frame, [self.contour], 0, self.color, self.lineThickness)
        else:
            raise NotImplementedError("The show function\
            does not currently support {} contour types".format(self.contourType))
        

    def writeCoordinatesToFile(self, path, frameIdx):
        """
        Writes parameters to file following:
        'frameNum', 'centreX', 'centreY', 'width', 'height', 'angle'
        
        :param str path: The destination path
        :param int frame: The frame number corresponding to the contour
        """
        with open(path, 'a') as outFile:
            outFile.write('{}\t'.format(frameIdx))
            outFile.write('{}\t{}\t'.format(*self.centre))
