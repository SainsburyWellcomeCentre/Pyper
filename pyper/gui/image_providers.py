# -*- coding: utf-8 -*-
"""
**************************
The image_providers module
**************************

This module provides subclasses of QQuickImageProvider to be used in the GUI module
The classes of this module supply sequences of images to the QT interface

:author: crousse
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('qt5agg')  # For OSX otherwise, the default backed doesn't allow to draw to buffer

from PyQt5.QtCore import QSize

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtQuick import QQuickImageProvider

from pyper.exceptions.exceptions import PyperNotImplementedError


class TrackingImageProvider(QQuickImageProvider):
    """
    Abstract class to supply image sequences (videos) to the QT interface
    """
    def __init__(self, requestedImType='img'):
        """
        :param string requestedImType: The type of image to return to the QT interface (one of ['img', 'pixmap'])
        """
        if requestedImType == 'img':
            imType = QQuickImageProvider.Image
        elif requestedImType == 'pixmap':
            imType = QQuickImageProvider.Pixmap
        else:
            raise PyperNotImplementedError('Unknown type: {}'.format(requestedImType))
        QQuickImageProvider.__init__(self, imType)
    
    def requestPixmap(self, id, qSize):
        """
        Returns the next image formated as a pixmap for QT with the associated QSize object
        """
        qimg, qSize = self.requestImage(id, qSize)
        img = QPixmap.fromImage(qimg)
        return img, qSize
        
    def requestImage(self, id, qSize):
        """
        Returns the next image formated as a QImage for QT with the associated QSize object
        """
        size = self.getSize(qSize)
        qimg = self.getBaseImg(size)
        return qimg, QSize(*size)
        
    def getSize(self, qSize):
        """
        Gets the qSize as a tuple of (width, height) (for openCV which flips x and y dimensions)
        If the input size is invalid it defaults to (512, 512)
        
        :param QSize qSize: The QT size object to convert
        :returns: size
        :rtype: tuple
        """
        return (qSize.width(), qSize.height()) if qSize.isValid() else (512, 512)
        
    def getRndmImg(self, size):
        """
        Generates a random image of size
        
        :param tuple size: The desired output image size
        :returns: The image
        """
        img = np.random.random(size)
        img *= 125
        img = img.astype(np.uint8)
        img = np.dstack([img]*3)
        return img
        
    def getBaseImg(self, size):
        raise PyperNotImplementedError("TrackingImageProvider missing method getBaseImg")


class CvImageProvider(TrackingImageProvider):
    """
    This class implements TrackingImageProvider for openCV images.
    If supplied it will use the stream's read() method to get the next image.
    If it cannot get an image, a random image (noise) of the proper size will be generated as
    a place holder.
    """
    
    def __init__(self, requestedImType='img', stream=None):
        """
        :param string requestedImType: The type of image to return to the QT interface (one of ['img', 'pixmap'])
        :param stream: An object that implements a read() method that returns an image and a current_frame_idx counter attribute
        """
        TrackingImageProvider.__init__(self, requestedImType=requestedImType)
        self._stream = stream
        
    def _writeErrorMsg(self, img, imgSize):
        """
        Write an error message on the image supplied as argument. The operation is performed in place
        
        :param img: The source image to write onto
        :param tuple imgSize: The size of the source image
        """
        text = "No contour found at frame: {}".format(self._stream.current_frame_idx)
        text2 = "Please check your parameters"
        text3 = "And ensure specimen is there"
        x = 10
        y = imgSize[0]/2
        ySpacing = 40
        yellow = (255, 255, 0)
        fontSize = 75/100.0
        cv2.putText(img, text, (x, y), 2, fontSize, yellow)
        y += ySpacing
        cv2.putText(img, text2, (x, y), 2, fontSize, yellow)
        y += ySpacing
        cv2.putText(img, text3, (x, y), 2, fontSize, yellow)

    def getBaseImg(self, size):
        """
        The method common to requestPixmap() and requestImage() to get the image from the stream before formatting
        
        :param tuple size: The desired image size
        :returns: the output image
        :rtype: QImage
        """
        if self._stream is not None:
            img = self._stream.read()
            if img is not None:
                img = img.color().copy()
                size = img.shape[:2]
            else:                
                img = self.getRndmImg(size)
                self._writeErrorMsg(img, size)
        else:
            img = self.getRndmImg(size)
        img = (img[:, :, :3]).copy() # For images with transparency channel, take only first 3 channels
        w, h = size
        qimg = QImage(img, h, w, QImage.Format_RGB888)
        return qimg


class PyplotImageProvider(TrackingImageProvider):
    """
    This class implements TrackingImageProvider for pyplot graphs.
    If supplied it will use the pyplot graph to get the next image.
    If it cannot get an image, a random image (noise) of the proper size will be generated as
    a place holder.
    """
    
    def __init__(self, requestedImType='pixmap', fig=None):
        """
        :param string requestedImType: The type of image to return to the QT interface (one of ['img', 'pixmap'])
        :param fig: A pyplot figure from which the image to return to QT will be extracted
        """
        TrackingImageProvider.__init__(self, requestedImType=requestedImType)
        self._fig = fig

    def getArray(self):
        """
        Return the graph drawn on self._fig as a raw rgb image (numpy array)
        """
        self._fig.canvas.draw()
        width, height = self._fig.canvas.get_width_height()
        img = self._fig.canvas.tostring_rgb()
        img = np.fromstring(img, dtype=np.uint8).reshape(height, width, 3)
        return img

    def getBaseImg(self, size):
        """
        The method common to requestPixmap() and requestImage() to get the image from the graph before formatting
        
        :param tuple size: The desired image size
        :returns: the output image
        :rtype: QImage
        """
        if self._fig is not None:
            img = self.getArray()
            size = img.shape[:2]
        else:
            img = self.getRndmImg(size)
        w, h = size
        qimg = QImage(img, h, w, QImage.Format_RGB888)
        return qimg
