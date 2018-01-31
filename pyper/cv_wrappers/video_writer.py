import cv2
import numpy as np

from pyper.exceptions.exceptions import PyperError


class VideoWriterFrameShapeError(PyperError):
    pass


class VideoWriterOpenError(PyperError):
    pass


class VideoWriter(object):
    """
    This class replicates the behaviour of the OpenCV 2.4 VideoWriter after wrapping it with exception handling
    """
    def __init__(self, save_path, codec, fps, frame_shape, is_color=False, transpose=False):  # FIXME: use n_color_channels
        self.save_path = save_path
        self.codec = codec
        self.fps = fps
        self.frame_shape = frame_shape
        self.is_color = is_color
        self.transpose = transpose  # whether we transpose a frame with the wrong orientation or raise an exception

        self.writer = cv2.VideoWriter(save_path, codec, fps, frame_shape, is_color)
        if not self.is_opened():
            raise VideoWriterOpenError("Could not open video writer. Codec {} probably unsupported.".format(codec))  # TODO do reverse of number
        # TODO: try other formats to guess and offer solution

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
            n_colors = frame.shape[2]
            if n_colors == 3:
                tmp_color_frame = frame
            elif n_colors == 1:
                tmp_color_frame = np.dstack([frame] * 3)
            else:
                err_msg = 'Wrong number of color channels, expected 1 or 3, got {}'.format(n_colors)
                raise VideoWriterFrameShapeError(err_msg)
            if not tmp_color_frame.dtype == np.uint8:
                tmp_color_frame = tmp_color_frame.astype(np.uint8)
            self.write(tmp_color_frame.copy())  # (copy because of dynamic arrays) # FIXME: slow
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
                print("WARNING: dimensions flipped, transposing frame")
                frame = np.transpose(frame, axes=(1, 0, 2))
                self.writer.write(frame.copy())
            else:
                raise VideoWriterFrameShapeError("Frame shape is {}, expected {}".
                                                 format(two_d_frame_shape, self.frame_shape))

