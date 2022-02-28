import os
import cv2
import numpy as np

from pyper.exceptions.exceptions import PyperError

try:
    from cv2 import cv
    fourcc = cv.CV_FOURCC
except ImportError:
    fourcc = cv2.VideoWriter_fourcc


class VideoWriterFrameShapeError(PyperError):
    pass


class VideoWriterOpenError(PyperError):
    pass


class VideoWriter(object):
    """
    This class replicates the behaviour of the OpenCV cv2.VideoWriter after wrapping it with exception handling
    """
    def __init__(self, save_path, codec_name, fps, frame_shape, is_color=False, transpose=False):  # FIXME: use n_color_channels
        self.save_path = save_path
        if isinstance(codec_name, int):  # REFACTOR:
            self.codec = codec_name
        else:
            self.codec = fourcc(*codec_name)
        self.fps = fps
        self.frame_shape = frame_shape
        self.is_color = is_color
        self.transpose = transpose  # whether we transpose a frame with the wrong orientation or raise an exception

        self.writer = cv2.VideoWriter(save_path, self.codec, fps, frame_shape, is_color)
        if not self.is_opened():
            container = os.path.splitext(self.save_path)[-1]
            raise VideoWriterOpenError("Could not open video writer."
                                       "Codec {} ({}) probably unsupported with container {}."
                                       .format(codec_name, self.codec, container))
        # TODO: use helpers to find alternative available codec/container pair

    def reset(self):
        self.release()
        self.open()

    def open(self):
        self.writer.open(self.save_path, self.codec, self.fps, self.frame_shape, self.is_color)
        if not self.is_opened():
            raise VideoWriterOpenError("Could not open video writer")

    def is_opened(self):
        return self.writer.isOpened()

    def release(self):
        self.writer.release()

    def save_frame(self, frame):
        """
        Saves the frame supplied as argument to self.video_writer

        :param frame: The frame to save
        :type frame: An image as an array with 1 or 3 color channels
        """
        if frame is not None and self.save_path is not None:
            if self.is_color:
                try:
                    n_colors = frame.shape[2]  # FIXME: extract from here and put in other class
                except IndexError:
                    raise VideoWriterFrameShapeError('No color axis found')

                if n_colors == 3:
                    output_frame = frame
                elif n_colors == 1:
                    output_frame = np.dstack([frame] * 3)
                else:
                    err_msg = 'Wrong number of color channels, expected 1 or 3, got {}'.format(n_colors)
                    raise VideoWriterFrameShapeError(err_msg)
            else:
                output_frame = frame
            if not output_frame.dtype == np.uint8:
                output_frame = output_frame.astype(np.uint8)
            self.write(output_frame.copy())  # (copy because of dynamic arrays) # FIXME: slow
        else:
            print("skipping save because {} is None".format("frame" if frame is None else "save_path"))

    # FIXME: deal with data type too
    def write(self, frame):  # FIXME: see for dynamic array (a.copy() to .write())
        """

        :param frame:
        :return:
        """
        two_d_frame_shape = frame.shape[:2]
        if two_d_frame_shape == self.frame_shape[::-1]:
            self.writer.write(frame)
            return
        else:
            if two_d_frame_shape == self.frame_shape and self.transpose:
                # print("WARNING: dimensions flipped, transposing frame")
                if self.is_color:
                    frame = np.transpose(frame, axes=(1, 0, 2))
                else:
                    frame = np.transpose(frame, axes=(1, 0))
                self.writer.write(frame.copy())
            else:
                raise VideoWriterFrameShapeError("Frame shape is {}, expected {} for writer of dimension {} "
                                                 "because of flipped dimensions in openCV".
                                                 format(two_d_frame_shape, self.frame_shape[::-1], self.frame_shape))

