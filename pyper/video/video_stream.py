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

import os, platform, sys

import numpy as np
import scipy

from video_frame import Frame
import cv2
from cv2 import cv
isPi = (platform.machine()).startswith('arm')
if isPi:
    import picamera.array
    from pyper.camera.camera import CvPiCamera

from pyper.exceptions.exceptions import VideoStreamIOException, VideoStreamTypeException, VideoStreamFrameException
    
DEFAULT_CAM = 0
CODEC = cv.CV_FOURCC(*'mp4v')  # TODO: check which codecs are available
FPS = 30
FRAME_SIZE = (256, 256)

IS_GRAPHICAL = 'PyQt5' in sys.modules.keys()


def update_progress_bar(val):
    modulo = val % 4
    if modulo == 0:
        sys.stdout.write('\b/')
    elif modulo == 1:
        sys.stdout.write('\b-')
    elif modulo == 2:
        sys.stdout.write('\b\\')
    elif modulo == 3:
        sys.stdout.write('\b|')
    sys.stdout.flush()


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
            self.size = FRAME_SIZE  # TODO: put as option
        
        self.bg_start_frame = bg_start
        self.bg_end_frame = self.bg_start_frame + n_background_frames - 1
        
        self.current_frame_idx = -1  # We start out since we increment upon frame loading
        
#    def __del__(self):
#        self.stopRecording("Recording stopped automatically")

    def _save(self, frame):
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
            writer_shape = tuple(list(self.size[::-1]) + [3])
            if tmp_color_frame.shape != writer_shape:
                raise VideoStreamFrameException("Cannot write frame of shape {} onto writer of shape {}"
                                                .format(tmp_color_frame.shape, writer_shape))
            else:
                self.video_writer.write(tmp_color_frame.copy())
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
        and a cv2.VideoWriter object to be used by _save()
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
        self._save(self.read())
        
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
        self.n_frames = self._get_n_frames(cv2.VideoCapture(file_path))
        self.size = self._get_frame_size(cv2.VideoCapture(file_path))
        VideoStream.__init__(self, file_path, bg_start, n_background_frames)
        self.fourcc = int(self.stream.get(cv.CV_CAP_PROP_FOURCC))
        self.fps = self._get_fps()
        self.duration = self.n_frames / float(self.fps)
        
    def _start_video_capture_session(self, file_path):  # TODO: refactor name
        """
        Initiates a cv2.VideoCapture object to supply the frames to read
        and a cv2.VideoWriter object to save a potential output
        
        :param str file_path: the source file path
        
        :return: capture and video_writer object
        :rtype: (cv2.VideoCapture, cv2.VideoWriter)
        """
        capture = cv2.VideoCapture(file_path)
        dirname, filename = os.path.split(file_path)
        # basename, ext = os.path.splitext(filename)
        save_path = os.path.join(dirname, 'recording.avi')  # Fixme: should use argument
        video_writer = cv2.VideoWriter(save_path, cv.CV_FOURCC(*'mp4v'), 15, self.size, True)
        if not(video_writer.isOpened()):
            raise VideoStreamIOException("Can't start video writer codec {} probably unsupported".format(CODEC))
        return capture, video_writer
    
    def _get_fps(self):
        """
        :return: The number of frames per seconds in the current recording
        :rtype: int
        """
        return int(self.stream.get(cv.CV_CAP_PROP_FPS))
        
    def _get_frame_size(self, stream):
        """
        Extract the frame size from the supplied stream
        
        :param stream: The stream to use as source
        :type stream: cv2.VideoCapture
        :return: width, height
        :rtype: (int, int)
        """
        self.width = int(stream.get(cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(stream.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
        return self.width, self.height
        
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
        n_frames = stream.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        if n_frames >= 1:  # We assume if the number is positive, the read was successful
            return n_frames
        else:
            n_frames = 0

        print("Computing number of frames, this may take some time.")
        while True:
            got_frame, _ = stream.read()
            if got_frame:
                if not IS_GRAPHICAL:
                    update_progress_bar(n_frames)
                n_frames += 1
            else:
                break
        if n_frames == 0:
            raise VideoStreamIOException("Could not read video")
        else:
            return n_frames
    
    def read(self):
        """
        Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: EOFError when end of stream is reached
        """
        self.current_frame_idx += 1
        if self.current_frame_idx > self.n_frames:
            raise EOFError("End of recording reached")
        got_frame, frame = self.stream.read()
        if got_frame:
            return Frame(frame.astype(np.float32))
        else:
            raise VideoStreamFrameException("Could not get frame at index {}".format(self.current_frame_idx))
        
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
        self.stream.set(cv.CV_CAP_PROP_POS_FRAMES, 0)
        self.current_frame_idx = -1
    

class UsbVideoStream(VideoStream):
    """
    A subclass of VideoStream for usb cameras supported by opencv
    It has a default frame size of 640,480 but user should not assume this to be accurate
    because some cameras refuse to change their frame size. In such cases,
    we defautl to the cameras default.
    """
    FRAME_SIZE = (640, 480)

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
        capture = cv2.VideoCapture(DEFAULT_CAM)
        capture.set(cv2.cv.CV_CAP_PROP_FPS, FPS)
        capture.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 100)

        # Try custom resolution
        width_set = capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, UsbVideoStream.FRAME_SIZE[0])
        height_set = capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, UsbVideoStream.FRAME_SIZE[1])
        
        # We now have to check because camera can silently refuse size setting (returns False)
        # We thus take whatever is now set (ours or the camera default)
        actual_width = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        actual_height = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
        if not width_set:
            print('Width refused by camera, using default of: {}'.format(actual_width))
        if not height_set:
            print('Height refused by camera, using default of: {}'.format(actual_height))

        actual_size = (actual_width, actual_height) # All in openCV nomenclature
        self.size = actual_size
        video_writer = cv2.VideoWriter(save_path, CODEC, FPS, actual_size)
        return capture, video_writer
        
    def read(self):
        """ Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: VideoStreamFrameException when no frame can be read
        """
        _, frame = self.stream.read()
        if frame is not None:
            self.current_frame_idx += 1
            return Frame(frame.astype(np.float32))
        else:
            raise VideoStreamFrameException("UsbVideoStream frame not found")
            
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
        self._cam.resolution = FRAME_SIZE[::-1]  # openCV flips dimensions
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
        video_writer = cv2.VideoWriter(save_path, CODEC, FPS, FRAME_SIZE)
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
        self.n_frames = self._get_n_frames(cv2.VideoCapture(file_path))
        self.size = self.frames[0].shape[:2]
        VideoStream.__init__(self, file_path, bg_start, n_background_frames)
        self.fourcc = int(self.stream.get(cv.CV_CAP_PROP_FOURCC))
        self.fps = self._get_fps()
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
            got_frame, frame = stream.read()
            if got_frame:
                n_frames += 1
                frame = scipy.misc.imresize(frame, 0.2, interp='bilinear')
                self.frames.append(frame)
            else:
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
