# -*- coding: utf-8 -*-
"""
**********************
The video_frame module
**********************

This module subclasses numpy to ease image analysis

:author: crousse
"""
import numpy as np
import cv2
from skimage.segmentation import clear_border
from scipy import misc

class Frame(np.ndarray):
    """
    A subclass of numpy ndarray that will have
    usefull methods for frame processing
    This is where all the image processing magic happens
    """
    def __new__(cls, input_array, name=''):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        frame = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        frame.name = name
        return frame

    def __array_finalize__(self, frame):
        # see InfoArray.__array_finalize__ for comments
        if frame is None: return
        self.name = getattr(frame, 'name', None)
        
    def _quitPressed(self):
        """
        Checks whether the user pressed 'esc' within the given timeout
        
        :return: Whether 'esc' was pressed
        :rtype: bool
        """
        kbdCode = cv2.waitKey(1)
        kbdCode = kbdCode&255
        return kbdCode == 27
        
    def blur(self, sigma=1.5):
        """
        Gaussian blurs a frame with a default sigma of 1.5
        
        :param float sigma: The sigma of the Gaussian filter (default 1.5)
        :return: the blured frame
        :rtype: `Frame`
        """
        return Frame(cv2.GaussianBlur(self, (15, 15), sigma))

    def denoise(self, kSize=3):
        """
        Median blurs a frame with a default kernel size of 3
        
        .. note:: kSize must be odd and > 1 (e.g. 3, 5, 7...)
        
        :param int kSize: The Kernel size of the median filter (default 3)
        :return: the denoised frame
        :rtype: `Frame`
        """
        return Frame(cv2.medianBlur(self, kSize))
        
    def gray(self):
        """
        Converts a frame to grayscale
        
        :return: the grayscale frame
        :rtype: `Frame`
        """
        if self.ndim == 2: # Single channel images:
            return Frame(np.dstack([self]*3))
        elif self.ndim == 3 and self.shape[2] == 1:
            raise NotImplementedError("Image is color but has only one channel.\
                                        This type is not supported yet")            
        return Frame(cv2.cvtColor(self, cv2.COLOR_BGR2GRAY))
        
    def color(self):
        """
        Converts a frame to a 3*8bits color frame
        
        :return: the color frame
        :rtype: `Frame`
        """
        if self.ndim == 3 and self.shape[2] in (3, 4): # Already color
            return Frame(self.astype(np.uint8))
#        return Frame(np.dstack([self.gray().astype(np.uint8)]*3))
        return Frame(self.gray())
        
    def threshold(self, threshold): #  TODO: autothreshold
        """
        Thresholds the frame using threshold (binary method)
        
        .. warning:: This will only work on 8 (or 3*8) bit images
        
        .. note:: For the above reason, the threshold must be 0<t<255
        
        :param int threshold: The threshold to use
        :return: the binary mask (8bits)
        :rtype: `Frame`
        """
#        code, silhouette = cv2.threshold(self, threshold, 255, cv2.THRESH_TOZERO)
        code, silhouette = cv2.threshold(self, threshold, 255, cv2.THRESH_BINARY)
        return Frame(silhouette)
        
    def normalise(self, refAvg=75):
        """
        Normalises the frame (divides by average and keeps 8 bits)
        
        :param int refAvg: The reference average to use to keep the 8 bits range
        
        :return: the normalised frame
        :rtype: `Frame`
        """
        avg = self.mean()
        originalDType = self.dtype
        frame = self.astype(np.float32)
        frame /= avg
        frame *= refAvg
        if originalDType != np.float32:
            frame = frame.astype(originalDType)
        return Frame(frame)
        
    def erode(self, iterations=2):
        """
        Performs erosion (for binary masks)
        
        .. warning:: should be applied to 8 bits masks
        
        :param int iterations: The number of times to run the erosion operation
        :return: the eroded mask
        :rtype: `Frame`
        """
        kernel = np.array([ [1/4., 1/2., 1/4.],
                            [1/2., 1/1., 1/2.],
                            [1/4., 1/2., 1/4.]])
        return Frame(cv2.erode(self, kernel, iterations=iterations))
        
    def clearBorders(self):
        """
        Removes the suprasthreshold pixels on the borders
        (for binary masks)
        
        .. warning:: should be applied to 8 bits masks
        
        :return: the eroded mask
        :rtype: `Frame`
        """
        return Frame(clear_border(self))
        
    def save(self, path):
        """
        Saves the frame to 'path'
        
        :param str path: the destination path
        """
        misc.imsave(path, self)
        
    def paint(self, text='', curve=[]):
        if text:
            cv2.putText(self, text, (5, 30), 2, 1, (255, 255, 255))
        if len(curve)>1:
            curve = np.int32([curve])
            cv2.polylines(self, curve, 0, (0, 255, 0))
        
    def display(self, winName='', text='', curve=[], delay=1, getCode=False):
        """
        Displays the frame using openCV
        potentially adds text and curve
        
        :param str winName: The name to give the system window the frame will be displayed in
        :param str text: The text to display at the bottom top of the image
        :param iterable curve: A list of points to be displayed on the image (in green)
        :param int delay: The time (ms) to wait for keyboard events during the display
        :param bool getCode: Whether to return the keyboard code
        
        :return: code (if option selected)
        :rtype: int
        
        :raises: KeyboardInterrupt if getCode == False and user presses 'esc'
        """
        self.paint(text, curve)
        if not winName:
            winName = self.name
        if self is not None:
            cv2.imshow(winName, self)
        if getCode:
            return cv2.waitKey(delay)
        else:
            if self._quitPressed():
                raise KeyboardInterrupt
