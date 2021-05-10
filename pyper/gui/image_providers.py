# -*- coding: utf-8 -*-
"""
**************************
The image_providers module
**************************

This module provides subclasses of QQuickImageProvider to be used in the GUI module
The classes of this module supply sequences of images to the QT interface

:author: crousse
"""

import numpy as np
import matplotlib
matplotlib.use('qt5agg')  # For OSX otherwise, the default backed doesn't allow to draw to buffer

from PyQt5.QtCore import QSize

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtQuick import QQuickImageProvider

from pyper.utilities.utils import write_structure_not_found_msg


def np_to_qimg(img, size):
    w, h = size
    if img.shape[2] == 3:
        qimg = QImage(img, h, w, img[0].nbytes, QImage.Format_RGB888)
    elif img.shape[2] == 4:
        qimg = QImage(img, h, w, img[0].nbytes, QImage.Format_RGBA8888)
    else:
        raise NotImplementedError('Unhandled image shape {}'.format(img.shape))
    return qimg


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
            raise NotImplementedError('Unknown type: {}'.format(requestedImType))
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
        raise NotImplementedError("TrackingImageProvider missing method getBaseImg")


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
        self.reuse_on_next_load = False  # reuse the current frame for the next load
        self.img = None

    def getBaseImg(self, size):
        """
        The method common to requestPixmap() and requestImage() to get the image from the stream before formatting
        
        :param tuple size: The desired image size
        :returns: the output image
        :rtype: QImage
        """
        if not self.reuse_on_next_load:
            if self._stream is not None:
                img = self._stream.read()
                # FIXME: check is hacky and implies dependency
                if hasattr(self._stream, 'should_update_vid'):  # It is a tracker (not viewer)
                    do_update = self._stream.should_update_vid
                else:
                    do_update = True

                if img is not None and do_update:
                    img = img.color()
                    size = img.shape[:2]
                elif self.img is not None:
                    img = self.img
                    size = img.shape[:2]
                else:
                    img = self.getRndmImg(size)
                    write_structure_not_found_msg(img, size, self._stream.current_frame_idx)
            else:
                img = self.getRndmImg(size)
                img = (img[:, :, :3]).copy()  # For images with transparency channel, take only first 3 channels
            self.img = img
        else:
            self.reuse_on_next_load = False
            if self.img is not None:
                img = self.img
                size = img.shape[:2]
            else:
                img = self.getRndmImg(size)
        return np_to_qimg(img, size)


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
        return np_to_qimg(img, size)
