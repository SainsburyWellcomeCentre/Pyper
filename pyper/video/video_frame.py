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
    useful methods for frame processing
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
        
    def _quit_pressed(self):
        """
        Checks whether the user pressed 'esc' within the given timeout
        
        :return: Whether 'esc' was pressed
        :rtype: bool
        """
        kbd_code = cv2.waitKey(1)
        kbd_code &= 255
        return kbd_code == 27
        
    def blur(self, sigma=1.5):
        """
        Gaussian blurs a frame with a default sigma of 1.5
        
        :param float sigma: The sigma of the Gaussian filter (default 1.5)
        :return: the blurred frame
        :rtype: video_frame.Frame
        """
        return Frame(cv2.GaussianBlur(self.copy(), (15, 15), sigma))

    def denoise(self, kernel_size=3):
        """
        Median blurs a frame with a default kernel size of 3
        
        .. note:: kSize must be odd and > 1 (e.g. 3, 5, 7...)
        
        :param int kernel_size: The Kernel size of the median filter (default 3)
        :return: the denoised frame
        :rtype: video_frame.Frame
        """
        return Frame(cv2.medianBlur(self.copy(), kernel_size))
        
    def gray(self, in_place=False):
        """
        Converts a frame to grayscale
        
        :return: the grayscale frame
        :rtype: video_frame.Frame
        """
        if self.ndim == 2:  # Single channel images:
            return Frame(np.dstack([self]*3))
        elif self.ndim == 3 and self.shape[2] == 1:
            return Frame(np.dstack([self[:, :, 0]] * 3))
        else:
            if in_place:
                return Frame(cv2.cvtColor(self, cv2.COLOR_BGR2GRAY))
            else:
                return Frame(cv2.cvtColor(self.copy(), cv2.COLOR_BGR2GRAY))
        
    def color(self, in_place=False):
        """
        Converts a frame to a 3*8bits color frame
        
        :return: the color frame
        :rtype: video_frame.Frame
        """
        if self.ndim == 3 and self.shape[2] in (3, 4):  # Already color
            if in_place:
                result = self
            else:
                result = self.copy()
            if result.dtype != np.uint8:
                return Frame(result.astype(np.uint8))
            else:
                return Frame(result)
#        return Frame(np.dstack([self.gray().astype(np.uint8)]*3))
        else:
            return Frame(self.gray(in_place))
        
    def threshold(self, threshold): #  TODO: autothreshold
        """
        Thresholds the frame using threshold (binary method)
        
        .. warning:: This will only work on 8 (or 3*8) bit images
        
        .. note:: For the above reason, the threshold must be 0<t<255
        
        :param int threshold: The threshold to use
        :return: the binary mask (8bits)
        :rtype: video_frame.Frame
        """
#        code, silhouette = cv2.threshold(self, threshold, 255, cv2.THRESH_TOZERO)
        code, silhouette = cv2.threshold(self, threshold, 255, cv2.THRESH_BINARY)
        return Frame(silhouette)
        
    def normalise(self, ref_avg=75):
        """
        Normalises the frame (divides by average and keeps 8 bits)
        
        :param int ref_avg: The reference average to use to keep the 8 bits range
        
        :return: the normalised frame
        :rtype: video_frame.Frame
        """
        avg = self.mean()
        original_dtype = self.dtype
        frame = self.astype(np.float32)
        frame /= avg
        frame *= ref_avg
        if original_dtype != np.float32:
            frame = frame.astype(original_dtype)
        return Frame(frame)
        
    def erode(self, iterations=2):
        """
        Performs erosion (for binary masks)
        
        .. warning:: should be applied to 8 bits masks
        
        :param int iterations: The number of times to run the erosion operation
        :return: the eroded mask
        :rtype: video_frame.Frame
        """
        kernel = np.array([
            [1/4., 1/2., 1/4.],
            [1/2., 1/1., 1/2.],
            [1/4., 1/2., 1/4.]
        ])
        return Frame(cv2.erode(self, kernel, iterations=iterations))
        
    def clear_borders(self):
        """
        Removes the supra-threshold pixels on the borders
        (for binary masks)
        
        .. warning:: should be applied to 8 bits masks
        
        :return: the eroded mask
        :rtype: video_frame.Frame
        """
        return Frame(clear_border(self))
        
    def save(self, path):
        """
        Saves the frame to 'path'
        
        :param str path: the destination path
        """
        misc.imsave(path, self)
        
    def paint(self, text='', curve=(), text_color=(255, 255, 255), curve_color=(0, 255, 0)):  # OPTIMISE:
        if text:
            text_origin = (5, 30)
            cv2.putText(self, text, text_origin, 2, 1, text_color)
        if len(curve) > 1 or isinstance(curve, np.ndarray):  # REFACTOR: clean up
            # OPTIMISE: probably slow function could be already in TrackingResults
            if not isinstance(curve, np.ndarray):
                curve = np.int32([curve])
            cv2.polylines(self, curve, 0, curve_color)
        
    def display(self, win_name='', text='', curve=(), delay=1, get_code=False):
        """
        Displays the frame using openCV
        potentially adds text and curve
        
        :param str win_name: The name to give the system window the frame will be displayed in
        :param str text: The text to display at the bottom top of the image
        :param iterable curve: A list of points to be displayed on the image (in green)
        :param int delay: The time (ms) to wait for keyboard events during the display
        :param bool get_code: Whether to return the keyboard code
        
        :return: code (if option selected)
        :rtype: int
        
        :raises: KeyboardInterrupt if getCode == False and user presses 'esc'
        """
        self.paint(text, curve)
        if not win_name:
            win_name = self.name
        if self is not None:
            cv2.imshow(win_name, self)
        if get_code:
            return cv2.waitKey(delay)
        else:
            if self._quit_pressed():
                raise KeyboardInterrupt
