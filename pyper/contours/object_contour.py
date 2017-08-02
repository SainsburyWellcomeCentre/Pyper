# -*- coding: utf-8 -*-
"""
*************************
The object_contour module
*************************

This module only hosts the ObjectContour class
This class makes it easier to extract contour features and draw them


:author: crousse
"""
from cv2 import ellipse as cv2_ellipse
from cv2 import fitEllipse, drawContours, moments

import numpy as np


class ObjectContour(object):
    """ A contour object to easily extract features from objects and draw """
    def __init__(self, contour, frame, contour_type='ellipse', color='w', line_thickness=1):
        """
        :param contour: The contour to make an ObjectContour
        :type contour: array of shape [nPoints, 1, 2]
        :param frame: The frame to draw the contour onto
        :type frame: an image
        :param str contour_type: The type to fit the contour (ellipse or raw) (not fit performed fot raw.
        :param str color: The color to draw the contour. One of 'w', 'r', 'g', 'b', 'y', 'm'.
        :param int line_thickness: The thickness in pixels of the line to draw the contour
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
        self.contour_type = contour_type
        self.color = colors[color]
        self.line_thickness = line_thickness
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
        if self.contour_type == 'ellipse':
            self.fit = fitEllipse(self.contour)
            self.centre = self.fit[0]
#           self.angle = np.round(self.ellipse[2], 1)
#           self.width, self.height = tuple(np.round(self.ellipse[1], 1))
        elif self.contour_type == 'raw':
            self.fit = moments(self.contour.astype(np.float32))  # FIXME: should not have to convert on the fly
            x = self.fit['m10'] / self.fit['m00']
            y = self.fit['m01'] / self.fit['m00']
            self.centre = (x, y)
        else:
            raise NotImplementedError("The show function\
            does not currently support {} contour types".format(self.contour_type))
        
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
