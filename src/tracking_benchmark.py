# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 21:08:59 2014

@author: crousse
"""

import timeit
import numpy as np


class Bench(object):
    def __init__(self):
        self.baseSetup = 'import cv2; import numpy as np; data = np.random.rand(640, 480)'
        
    def blur(self, iterN=100):
        numpySetup = self.baseSetup + '; from scipy import ndimage'
        numpyCmd = 'test=ndimage.gaussian_filter(data, truncate=2, sigma=2)'
        print timeit.timeit(setup=numpySetup, stmt=numpyCmd, number=iterN)/iterN
        
        cv2Setup = self.baseSetup + '; import cv2'
        cv2Cmd = 'test=cv2.GaussianBlur(data, (15, 15), 2)'
        print timeit.timeit(setup=cv2Setup, stmt=cv2Cmd, number=iterN)
        
    def diff(self, iterN=100):
        baseSetup = self.baseSetup +  '; bcg=np.random.rand(640, 480)'
        cv2Cmd = 'test=cv2.absdiff(bcg, data)'
        numpyCmd = 'test=data - bcg'
    
        print timeit.timeit(setup=baseSetup, stmt=numpyCmd, number=iterN)/iterN
        print timeit.timeit(setup=baseSetup, stmt=cv2Cmd, number=iterN)/iterN


class Frame(np.ndarray):

    def __new__(cls, input_array, info=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.info = info
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.info = getattr(obj, 'info', None)