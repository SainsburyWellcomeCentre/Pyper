# -*- coding: utf-8 -*-
"""
**************************
The image_providers module
**************************

This module provides subclasses of QQuickImageProvider to be used in the GUI module

:author: crousse
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('qt5agg') # For OSX otherwise, the default backed doesn't allow to draw to buffer

from PyQt5.QtCore import QSize

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtQuick import QQuickImageProvider

class CvImageProvider(QQuickImageProvider):
    
    def __init__(self, requestedImType='img', stream=None):
        if requestedImType == 'img':
            imType = QQuickImageProvider.Image
        elif requestedImType == 'pixmap':
            imType = QQuickImageProvider.Pixmap
        else:
            raise NotImplementedError('Unknown type: {}'.format(requestedImType))
        QQuickImageProvider.__init__(self, imType)
        self._stream = stream

    def requestPixmap(self, id, qSize):
        """
        Called if imType == Pixmap
        """
        qimg, qSize = self.requestImage(id, qSize)
        img = QPixmap.fromImage(qimg)
        return img, qSize
        
    def requestImage(self, id, qSize):
        """
        Called if imType == Image
        """
        size = self.getSize(qSize)
        qimg = self.getBaseImg(size)
        return qimg, QSize(*size)
        
    def getSize(self, qSize):
        if qSize.isValid():
            size = (qSize.width(), qSize.height())
        else:
            size = (512, 512)
        return size
        
    def getRndmImg(self, size):
        img = np.random.random(size)
        img *= 125
        img = img.astype(np.uint8)
        img = np.dstack([img]*3)
        return img
        
    def _writeErrorMsg(self, img, imgSize):
        text = "No contour found at frame: {}".format(self._stream.currentFrameIdx)
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

class PyplotImageProvider(QQuickImageProvider):
    
    def __init__(self, fig=None):
        QQuickImageProvider.__init__(self, QQuickImageProvider.Pixmap)
        self._fig = fig

    def requestPixmap(self, id, qSize):
        """
        Called if imType == Pixmap
        """
        qimg, qSize = self.requestImage(id, qSize)
        img = QPixmap.fromImage(qimg)
        return img, qSize
        
    def requestImage(self, id, qSize):
        """
        Called if imType == Image
        """
        size = self.getSize(qSize)
        qimg = self.getBaseImg(size)
        return qimg, QSize(*size)
        
    def getSize(self, qSize):
        return (qSize.width(), qSize.height()) if qSize.isValid() else (512, 512)
        
    def getRndmImg(self, size):
        img = np.random.random(size)
        img *= 125
        img = img.astype(np.uint8)
        img = np.dstack([img]*3)
        return img
        
    def getArray(self):
        self._fig.canvas.draw()
        width, height = self._fig.canvas.get_width_height()
        img = self._fig.canvas.tostring_rgb()
        img = np.fromstring(img, dtype=np.uint8).reshape(height, width, 3)
        return img

    def getBaseImg(self, size):
        if self._fig is not None:
            img = self.getArray()
            size = img.shape[:2]
        else:
            img = self.getRndmImg(size)
        w, h = size
        qimg = QImage(img, h, w, QImage.Format_RGB888)
        return qimg
