# -*- coding: utf-8 -*-
"""
***********************
The video_stream module
***********************

The second main module after tracking.
It allows
This module used inspiration from code developed by Andrew Erskine for the UsbVideoStream class
and from Antonio Gonzalez for the RecordedVideoStream class

:author: crousse
"""

import numpy as np
import os
import platform
import scipy
import sys
from cv2 import cv

import cv2

from pyper.video.video_frame import Frame
from pyper.utilities.utils import spin_progress_bar
from pyper.exceptions.exceptions import VideoStreamIOException, VideoStreamTypeException, VideoStreamFrameException
from pyper.cv_wrappers.video_writer import VideoWriter
from pyper.cv_wrappers.video_capture import VideoCapture, VideoCaptureGrabError, VideoCapturePropertySetError

IS_PI = (platform.machine()).startswith('arm')
if IS_PI:
    import picamera.array
    from pyper.camera.camera import CvPiCamera

    
DEFAULT_CAM = 0
CODEC = cv.CV_FOURCC(*'mp4v')  # TODO: check which codecs are available
FPS = 30
DEFAULT_FRAME_SIZE = (256, 256)

IS_GRAPHICAL = 'PyQt5' in sys.modules.keys()


class VideoStream(object):
    """
    A video stream which is supposed to be subclassed for use
    """
    def __init__(self, save_path, bg_start, n_background_frames):
        """
        :param str save_path: The path to save the video to (should end in container extension)
        :param int bg_start: The frame to use as background frames range start
        :param int n_background_frames: The number of frames to use for the background
        """
        self.save_path = save_path
        self._init_cam()
        self.stream, self.video_writer = self._start_video_capture_session(self.save_path)
        if not hasattr(self, 'size'):
            self.size = DEFAULT_FRAME_SIZE  # TODO: put as option
        
        self.bg_start_frame = bg_start
        self.bg_end_frame = self.bg_start_frame + n_background_frames - 1
        
        self.current_frame_idx = -1  # We start out since we increment upon frame loading
        self.seekable = False

    def save(self, frame):  # FIXME: fix video_writer calls (put most in VideoWriter)
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
                tmp_color_frame = np.dstack([frame]*3)
            else:
                err_msg = 'Wrong number of color channels, expected 1 or 3, got {}'.format(n_colors)
                raise VideoStreamTypeException(err_msg)
            if not tmp_color_frame.dtype == np.uint8:
                tmp_color_frame = tmp_color_frame.astype(np.uint8)
            self.video_writer.write(tmp_color_frame.copy())  # (copy because of dynamic arrays) # FIXME: slow
        else:
            print("skipping save because {} is None".format("frame" if frame is None else "save_path"))
            
    def _init_cam(self):
        pass
        
    def read(self):
        """ Should return the next frame .
        This is one of the methods that are expected to change the most between 
        implementations. """
        raise NotImplementedError('This method should be defined by subclasses')
    
    def _start_video_capture_session(self, src_path):
        """ Should return a stream of frames to be used by read()
        and a cv2.VideoWriter object to be used by save()
        This is one of the methods that are expected to change the most between 
        implementations. """
        raise NotImplementedError('This method should be defined by subclasses')
            
    def is_bg_frame(self):
        """
        Checks if the current frame is in the background frames range
        
        :return: Whether the current frame is in the background range
        :rtype: bool
        """
        return self.bg_start_frame <= self.current_frame_idx <= self.bg_end_frame
    
    def record_current_frame_to_disk(self):
        """ Saves current frame to video file (self.dest) """
        self.save(self.read())
        
    def stop_recording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to display upon stoping the recording.
        """
        print(msg)
        self.video_writer.release()
        cv2.destroyAllWindows()


class RecordedVideoStream(VideoStream):
    """
    A subclass of VideoStream that supplies the frames from a
    video file
    """
    def __init__(self, file_path, bg_start, n_background_frames):
        """
        :param str file_path: The source file path to read for the video
        :param int bg_start: The frame to use as background frames range start
        :param int n_background_frames: The number of frames to use for the background
        """
        tmp_capture = VideoCapture(file_path)
        self.n_frames = self._get_n_frames(tmp_capture)  # FIXME: writer and capture calls
        self.width = tmp_capture.frame_width
        self.height = tmp_capture.frame_height
        self.size = self.width, self.height
        self.fps = tmp_capture.fps
        self.fourcc = tmp_capture.fourcc  # Check if should come from self.stream or same
        self.duration = self.n_frames / float(self.fps)

        VideoStream.__init__(self, file_path, bg_start, n_background_frames)
        self.seekable = self.stream.seekable
        
    def _start_video_capture_session(self, file_path):  # TODO: refactor name
        """
        Initiates a cv2.VideoCapture object to supply the frames to read
        and a cv2.VideoWriter object to save a potential output
        
        :param str file_path: the source file path
        
        :return: capture and video_writer object
        :rtype: (cv2.VideoCapture, cv2.VideoWriter)
        """
        capture = VideoCapture(file_path)
        dirname, filename = os.path.split(file_path)
        # basename, ext = os.path.splitext(filename)
        save_path = os.path.join(dirname, 'recording.avi')  # Fixme: should use argument
        video_writer = VideoWriter(save_path, cv.CV_FOURCC(*'mp4v'), 15, self.size, True)
        return capture, video_writer
        
    def _get_n_frames(self, stream):
        """
        Returns the number of frames in the stream
        Compensates for some bug in OpenCV in finding
        that info in the metadata
        
        :param VideoCapture stream: The stream to use as source
        
        :return: the number of frames in the stream
        :rtype: int
        
        :raises: VideoStreamIOException if video cannot be read
        """
        n_frames = stream.n_frames
        if n_frames >= 1:  # We assume if the number is positive, the read was successful
            return n_frames
        else:
            n_frames = 0

        print("Computing number of frames, this may take some time.")
        while True:
            try:
                stream.read()
                if not IS_GRAPHICAL:
                    spin_progress_bar(n_frames)
                n_frames += 1
            except VideoCaptureGrabError as err:
                break
        if n_frames == 0:
            raise VideoStreamIOException("Could not read video")
        else:
            return n_frames

    def seek(self, frame_id):
        self.stream.seek(frame_id)  # FIXME: because of read
        self.current_frame_idx = frame_id
    
    def read(self):  # OPTIMISE: (cast)
        """
        Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: EOFError when end of stream is reached
        """
        self.current_frame_idx += 1
        if self.current_frame_idx > self.n_frames:
            raise EOFError("End of recording reached")
        frame = self.stream.read()
        return Frame(frame.astype(np.float32))  # TODO: see if should change exception to VideoStreamFrameException
        
    def time_str_to_frame_idx(self, time_str):
        """
        timeStr Time string in format mm:ss.
        Returns the frame number that corresponds to that time.
        
        :param str time_str: A string of the form 'mm:ss'
        
        :return Idx: The corresponding frame index
        :rtype: int
        """
        time_str = time_str.split(':')
        if len(time_str) == 2:
            minutes, seconds = time_str
            seconds = (int(minutes) * 60) + int(seconds)
        else:
            raise NotImplementedError
        return seconds * self.fps
        
    def stop_recording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to print on closing.
        """
        VideoStream.stop_recording(self, msg)
        self.stream.reset()
        self.current_frame_idx = -1
    

class UsbVideoStream(VideoStream):
    """
    A subclass of VideoStream for usb cameras supported by opencv
    It has a default frame size of 640,480 but user should not assume this to be accurate
    because some cameras refuse to change their frame size. In such cases,
    we defautl to the cameras default.
    """
    DEFAULT_FRAME_SIZE = (640, 480)

    def __init__(self, save_path, bg_start, n_background_frames):
        """
        :param str save_path: The destination file path to save the video to
        :param int bg_start: The frame to use as background frames range start
        :param int n_background_frames: The number of frames to use for the background
        """
        VideoStream.__init__(self, save_path, bg_start, n_background_frames)
        
    def _start_video_capture_session(self, save_path):
        """
        Initiates a cv2.VideoCapture object to supply the frames to read
        (from the default usb camera)
        and a cv2.VideoWriter object to save a potential output
        
        :param str filePath: the destination file path
        
        :return: capture and video_writer object
        :type: (cv2.VideoCapture, cv2.VideoWriter)
        """
        capture = VideoCapture(DEFAULT_CAM)
        try:
            capture.set("fps", FPS)
        except VideoCapturePropertySetError:
            print("WARNING: could not set FPS to {}. Defaulting to {}.".format(FPS, capture.fps))
        try:
            capture.set("BRIGHTNESS", 100)
        except VideoCapturePropertySetError:
            print("WARNING: could not set brightness to {}. Defaulting to {}.".format(100, capture.get('brightness')))

        # Try custom resolution
        try:
            capture.width = UsbVideoStream.DEFAULT_FRAME_SIZE[0]
            actual_width = capture.width
        except VideoCapturePropertySetError:
            # We now have to check because camera can silently refuse size setting (returns False)
            # We thus take whatever is now set (ours or the camera default)
            actual_width = capture.frame_width
            print('Width refused by camera, using default of: {}'.format(actual_width))

        try:
            capture.height = UsbVideoStream.DEFAULT_FRAME_SIZE[1]
            actual_height = capture.height
        except VideoCapturePropertySetError:
            actual_height = capture.height
            print('Height refused by camera, using default of: {}'.format(actual_height))

        actual_size = (actual_width, actual_height)  # All in openCV nomenclature
        self.size = actual_size
        video_writer = VideoWriter(save_path, CODEC, FPS, actual_size, is_color=True)
        return capture, video_writer
        
    def read(self):
        """ Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: VideoStreamFrameException when no frame can be read
        """
        try:
            frame = self.stream.read()
        except VideoCaptureGrabError:
            raise VideoStreamFrameException("UsbVideoStream frame not found")
        self.current_frame_idx += 1
        return Frame(frame.astype(np.float32))
            
    def stop_recording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to print upon closing.
        """
        self.stream.release()
        VideoStream.stop_recording(self, msg)
        self.current_frame_idx = -1


class PiVideoStream(VideoStream):
    """
    A subclass of VideoStream for the raspberryPi camera
    which isn't supported by opencv
    """
    def __init__(self, save_path, bg_start, n_background_frames):
        """
        :param str save_path: The destination file path to save the video to
        :param int bg_start: The frame to use as background frames range start
        :param int n_background_frames: The number of frames to use for the background
        """
        VideoStream.__init__(self, save_path, bg_start, n_background_frames)

    def _init_cam(self):
        """
        Initialises the CvPiCamera object to provide the frames
        """
        self._cam = CvPiCamera()
        self._cam.resolution = DEFAULT_FRAME_SIZE[::-1]  # openCV flips dimensions
        if os.getuid() == 0:
            self._cam.led = False
        else:
            print("LED kept on. To turn off run as root")
        
    def _start_video_capture_session(self, save_path):
        """
        Initiates a picamera.array.PiRGBArray object to store
        the frames from the picamera when reading 
        and a cv2.VideoWriter object to save a potential output
        
        :param str save_path: the destination file path
        
        :return: array and video_writer object
        :type: (picamera.array.PiRGBArray, cv2.VideoWriter)
        """
        video_writer = VideoWriter(save_path, CODEC, FPS, DEFAULT_FRAME_SIZE)
        stream = picamera.array.PiRGBArray(self._cam)
        return stream, video_writer
        
    def read(self):
        """
        Returns the next frame after updating the count
        
        :return: A video frame
        :rtype: video_frame.Frame
        """
        stream = self.stream
        self._cam.quick_capture(stream)
        # stream.array now contains the image data in BGR order
        frame = stream.array
        stream.truncate(0)
        self.current_frame_idx += 1
        return Frame(frame.astype(np.float32))
        
    def restart_recording(self, reset):
        """
        Restarts the camera and potentially resets the output stream and frame index
        
        :param bool reset: Whether to reset the output stream (overwrite previous) and frame index
        """
        if self._cam.closed:
            self._init_cam()
        if reset:
            self.stream, self.video_writer = self._start_video_capture_session(self.save_path)
            self.current_frame_idx = -1
    
    def stop_recording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to print before closing.
        """
        VideoStream.stop_recording(self, msg)
        self._cam.close_encoder()
        self._cam.close()

    
class QuickRecordedVideoStream(RecordedVideoStream):
    """
    A subclass of RecordedVideoStream that supplies the frames from a
    video file but allows seeking (downscales the video (* 0.2) and loads everything in a numpy array.
    """
    def __init__(self, file_path, bg_start, n_background_frames):
        """
        :param str file_path: The source file path to read for the video
        :param int bg_start: The frame to use as background frames range start
        :param int n_background_frames: The number of frames to use for the background
        """
        tmp_capture = VideoCapture(file_path)
        self.n_frames = self._get_n_frames(tmp_capture)
        self.size = self.frames[0].shape[:2]
        VideoStream.__init__(self, file_path, bg_start, n_background_frames)
        self.fourcc = self.stream.fourcc
        self.fps = self.stream.fps
        self.duration = self.n_frames / float(self.fps)
        
    def _get_n_frames(self, stream):
        """
        Returns the number of frames in the stream
        Compensates for some bug in opencv in finding
        that info in the metadata
        
        :param stream: The stream to use as source
        :type stream: stream that supports read()
        
        :return: the number of frames in the stream
        :rtype: int
        
        :raises: VideoStreamIOException if video cannot be read
        """
        n_frames = 0
        self.frames = []
        while True:
            try:
                frame = stream.read()
                n_frames += 1
                frame = scipy.misc.imresize(frame, 0.2, interp='bilinear')  # FIXME: parametrise resizing factor
                self.frames.append(frame)
            except VideoCaptureGrabError:
                break
        if n_frames == 0:
            raise VideoStreamIOException("Could not read video")
        else:
            return n_frames
    
    def read(self, idx=None):
        """
        Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: EOFError when end of stream is reached
        """
        if idx is None:
            self.current_frame_idx += 1
        else:
            self.current_frame_idx = idx
        if self.current_frame_idx > self.n_frames:
            raise EOFError("End of recording reached")
        frame = self.frames[self.current_frame_idx]
        return Frame(frame)


class ImageListVideoStream(object):
    """
    A minimalist VideoStream it just implements the read() method to return images from a list
    """
    def __init__(self, imgs_list):
        """
        :param list imgs_list: The list of images constituting the stream
        """
        self.imgs = imgs_list
        self.current_frame_idx = 0

    def read(self):
        """
        Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: EOFError when end of stream is reached
        """
        if self.current_frame_idx > (len(self.imgs) - 2):
            raise EOFError("End of recording reached")
        img = self.imgs[self.current_frame_idx]
        frame = Frame(img)
        self.current_frame_idx += 1
        return frame
