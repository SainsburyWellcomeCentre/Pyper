"""
*********************
The transcoder module
*********************

This module is supplied as a utility to convert between openCV video formats to open videos with different players
This may be required if your player doesn't support your format or to fix some videos if some metadata are missing in the file

:author: crousse
"""

import numpy as np
from scipy.misc import imresize
import cv2
from cv2 import cv

from video_stream import RecordedVideoStream

from progressbar import Percentage, Bar, ProgressBar


class Transcoder(RecordedVideoStream):
    """
    The transcoder class.
    
    It will convert the video to mp4v (destFilePath should match this extension) but this can be changed easily.
    You can also crop and scale the video at the same time.
    """
    def __init__(self, src_file_path, dest_file_path, bg_start, n_background_frames, crop_params, scale_params):
        RecordedVideoStream.__init__(self, src_file_path, bg_start, n_background_frames)
        self.crop_params = np.array(crop_params)
        self.scale_params = np.array(scale_params)
        size = self.get_final_size()
        self.video_writer = cv2.VideoWriter(dest_file_path,
                                            cv.CV_FOURCC(*'mp4v'),  # FIXME: Format as argument
                                            self.fps,
                                            size[::-1],
                                            True)
        # FIXME: add roi
        # FIXME: add reader
    
    def get_final_size(self):
        cropped_width = self.size[0] - sum(self.crop_params[0])
        cropped_height = self.size[1] - sum(self.crop_params[1])
        cropped_size = np.array((cropped_width, cropped_height))

        final_size = cropped_size * self.scale_params
        final_size = tuple(final_size.astype(np.uint32))
        return final_size
    
    def transcode(self):
        crop_params = self.crop_params
        final_width, final_height = self.get_final_size()
        widgets = ['Encoding Progress: ', Percentage(), Bar()]  # FIXME: only if CLI (put option in __init__
        pbar = ProgressBar(widgets=widgets, maxval=self.n_frames).start()
        for i in range(self.n_frames):
            pbar.update(i)
            frame = self.read()
            frame = frame[crop_params[0][0]: -crop_params[0][1], crop_params[1][0]: -crop_params[1][1]]
            scale = np.concatenate((self.scale_params, np.array([1]))) * frame.shape
            frame = imresize(frame, scale.astype(int), interp='bilinear')
            self.video_writer.write(frame)
#            self.video_writer.write(np.uint8(np.dstack([frame]*3)))
        pbar.finish()
        self.video_writer.release()
        self.video_writer = None
