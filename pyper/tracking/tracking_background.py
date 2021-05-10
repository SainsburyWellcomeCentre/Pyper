import numpy as np

import cv2

from pyper.video.video_frame import Frame


class Background(object):
    def __init__(self, n_sds):
        self.data = None
        self.std = None
        self.source = None
        self.global_avg = None
        self.n_sds = n_sds
        self.use_sd = False

    def clear(self):
        self.data = None
        self.std = None
        self.source = None
        self.global_avg = None
        self.n_sds = 2
        self.use_sd = False

    def build(self, frame, color=False):
        if __debug__:
            print("Building background")
        bg = frame.denoise().blur()
        if not color:
            bg = bg.gray()
        if self.source is None:
            if self.data is None:
                self.data = bg
            else:
                self.data = Frame(np.dstack((self.data, bg)))  # FIXME: won't work for colour
        else:
            self.data = Frame(self.source.astype(np.float32))
            self.data = self.data.denoise().blur()
            if not color:
                self.data = self.data.gray()
            if self.data.ndim == 3 and not color:
                self.data = self.data.mean(2)

    def finalise(self):
        """
        Finalise the background (average stack and compute SD if more than one image)
        """
        if self.data.ndim > 2:
            self.get_std()
            self.flatten()
        self.global_avg = self.data.mean()

    def get_std_threshold(self):
        """
        Get threshold for std tracking method
        :return:
        """
        return self.std * self.n_sds

    def diff(self, frame):  # WARNING: shape of frame and self.data must match
        return Frame(cv2.absdiff(frame, self.data))

    def to_mask(self, threshold):
        bg = self.data.copy()
        bg = bg.astype(np.uint8)
        mask = bg.threshold(threshold)
        return mask

    def flatten(self):
        self.data = self.data.mean(2)

    def get_std(self):
        self.std = np.std(self.data, axis=2)
        self.use_sd = True
