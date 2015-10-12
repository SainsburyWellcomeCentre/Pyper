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
    from camera import CvPiCamera
    
DEFAULT_CAM = 0
CODEC = cv.CV_FOURCC(*'mp4v') # TODO: check which codecs are available
FPS = 30
FRAME_SIZE = (256, 256)

def pBar(val):
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
    def __init__(self, savePath, bgStart, nBackgroundFrames):
        """
        :param str savePath: The path to save the video to (should end in container extension)
        :param int bgStart: The frame to use as background frames range start
        :param int nBackgroundFrames: The number of frames to use for the background
        """
        self.savePath = savePath
        self._init_cam()
        self.stream, self.videoWriter = self._startVideoCaptureSession(self.savePath)
        if not hasattr(self, 'size'):
            self.size = FRAME_SIZE # TODO: put as option
        
        self.bgStartFrame = bgStart
        self.bgEndFrame = self.bgStartFrame + nBackgroundFrames - 1
        
        self.currentFrameIdx = -1 # We start out since we increment upon frame loading
        
#    def __del__(self):
#        self.stopRecording("Recording stopped automatically")

    def _save(self, frame):
        """
        Saves the frame supplied as argument to self.videoWriter
        
        :param frame: The frame to save
        :type frame: An image as an array with 1 or 3 color channels
        """
        if frame is not None and self.savePath is not None:
            nColors = frame.shape[2]
            if nColors == 3:
                tmpColorFrame = frame
            elif nColors == 1:
                tmpColorFrame = np.dstack([frame]*3)
            else:
                errMsg = 'Wrong number of color channels, expexted 1 or 3, got {}'.format(nColors)
                raise VideoStreamTypeException(errMsg)
            # TODO: assert shape
            if not tmpColorFrame.dtype == np.uint8:
                tmpColorFrame = tmpColorFrame.astype(np.uint8)
            self.videoWriter.write(tmpColorFrame.copy())
        else:
            print("skipping save because {} is None".format("frame" if frame is None else "savepath"))
            
    def _init_cam(self):
        pass
        
    def read(self):
        """ Should return the next frame .
        This is one of the methods that are expected to change the most between 
        implementations. """
        raise NotImplementedError('This method should be defined by subclasses')
    
    def _startVideoCaptureSession(self, srcPath):
        """ Should return a stream of frames to be used by read()
        and a cv2.VideoWriter object to be used by _save()
        This is one of the methods that are expected to change the most between 
        implementations. """
        raise NotImplementedError('This method should be defined by subclasses')
            
    def isBgFrame(self):
        """
        Checks if the current frame is in the background frames range
        
        :return: Whether the current frame is in the background range
        :rtype: bool
        """
        return (self.bgStartFrame <= self.currentFrameIdx <= self.bgEndFrame)
    
    def recordCurrentFrameToDisk(self):
        """ Saves current frame to video file (self.dest) """
        self._save(self.read())
        
    def stopRecording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to display upon stoping the recording.
        """
        print(msg)
        self.videoWriter.release()
        cv2.destroyAllWindows()
    
class RecordedVideoStream(VideoStream):
    """
    A subclass of VideoStream that supplies the frames from a
    video file
    """
    def __init__(self, filePath, bgStart, nBackgroundFrames):
        """
        :param str filePath: The source file path to read for the video
        :param int bgStart: The frame to use as background frames range start
        :param int nBackgroundFrames: The number of frames to use for the background
        """
        self.nFrames = self._getNFrames(cv2.VideoCapture(filePath))
        self.size = self._getFrameSize(cv2.VideoCapture(filePath))
        VideoStream.__init__(self, filePath, bgStart, nBackgroundFrames)
        self.fourcc = int(self.stream.get(cv.CV_CAP_PROP_FOURCC))
        self.fps = self._getFps()
        self.duration = self.nFrames / float(self.fps)
        
    def _startVideoCaptureSession(self, filePath): # TODO: refactor name
        """
        Initiates a cv2.VideoCapture object to supply the frames to read
        and a cv2.VideoWriter object to save a potential output
        
        :param str filePath: the source file path
        
        :return: capture and videoWriter object
        :rtype: (cv2.VideoCapture, cv2.VideoWriter)
        """
        capture = cv2.VideoCapture(filePath)
        dirname, filename = os.path.split(filePath)
        basename, ext = os.path.splitext(filename)
        savePath = os.path.join(dirname, 'recording.avi') # Fixme: should use argument
        videoWriter = cv2.VideoWriter(savePath, cv.CV_FOURCC(*'mp4v'), 15, self.size, True)
        if not(videoWriter.isOpened()):
            raise VideoStreamIOException("Can't start video writer codec {} probably unsupported".format(CODEC))
        return capture, videoWriter
    
    def _getFps(self):
        """
        :return: The number of frames per seconds in the current recording
        :rtype: int
        """
        return int(self.stream.get(cv.CV_CAP_PROP_FPS))
        
    def _getFrameSize(self, stream):
        """
        Extract the frame size from the supplied stream
        
        :param stream: The stream to use as source
        :type stream: cv2.VideoCapture
        :return: width, height
        :rtype: (int, int)
        """
        self.width = int(stream.get(cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(stream.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
        return (self.width, self.height)
        
    def _getNFrames(self, stream):
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
        nFrames = 0
        print("Computing number of frames, this may take some time.  ")
        while True:
            gotFrame, _ = stream.read()
            if gotFrame:
                pBar(nFrames)
                nFrames +=1
            else:
                break
        print("\nDone")
        if nFrames == 0:
            raise VideoStreamIOException("Could not read video")
        else:
            return nFrames
    
    def read(self):
        """
        Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: EOFError when end of stream is reached
        """
        self.currentFrameIdx += 1
        if self.currentFrameIdx > self.nFrames:
            raise EOFError("End of recording reached")
        gotFrame, frame = self.stream.read()
        if gotFrame:
            return Frame(frame.astype(np.float32))
        else:
            raise VideoStreamFrameException("Could not get frame at index {}".format(self.currentFrameIdx))
        
    def timeStrToFrameIdx(self, timeStr):
        """
        timeStr Time string in format mm:ss.
        Returns the frame number that corresponds to that time.
        
        :param str timeStr: A string of the form 'mm:ss'
        
        :return Idx: The corresponding frame index
        :rtype: int
        """
        timeStr = timeStr.split(':')
        if len(timeStr) == 2:
            minutes, seconds = timeStr
            seconds = (int(minutes) * 60) + int(seconds)
        else:
            raise NotImplementedError
        return seconds * self.fps
        
    def stopRecording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to print on closing.
        """
        VideoStream.stopRecording(self, msg)
        self.stream.set(cv.CV_CAP_PROP_POS_FRAMES, 0)
        self.currentFrameIdx = -1
    

class UsbVideoStream(VideoStream):
    """
    A subclass of VideoStream for usb cameras supported by opencv
    It has a default frame size of 640,480 but user should not assume this to be accurate
    because some cameras refuse to change their frame size. In such cases,
    we defautl to the cameras default.
    """
    FRAME_SIZE = (640, 480)
    def __init__(self, savePath, bgStart, nBackgroundFrames):
        """
        :param str filePath: The destination file path to save the video to
        :param int bgStart: The frame to use as background frames range start
        :param int nBackgroundFrames: The number of frames to use for the background
        """
        VideoStream.__init__(self, savePath, bgStart, nBackgroundFrames)
        
    def _startVideoCaptureSession(self, savePath):
        """
        Initiates a cv2.VideoCapture object to supply the frames to read
        (from the default usb camera)
        and a cv2.VideoWriter object to save a potential output
        
        :param str filePath: the destination file path
        
        :return: capture and videoWriter object
        :type: (cv2.VideoCapture, cv2.VideoWriter)
        """
        capture = cv2.VideoCapture(DEFAULT_CAM)
        capture.set(cv2.cv.CV_CAP_PROP_FPS, FPS)
        capture.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 100)

        # Try custom resolution
        widthSet = capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, UsbVideoStream.FRAME_SIZE[0])
        heightSet = capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, UsbVideoStream.FRAME_SIZE[1])
        
        if not widthSet: # We now have to check because camera can silently refuse size setting (returns False)
            # In this case, we take the camera default
            actualWidth = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        if not heightSet:
            actualHeight = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        actualSize = (actualWidth, actualHeight) # All in openCV nomenclature
        self.size = actualSize
        videoWriter = cv2.VideoWriter(savePath, CODEC, FPS, actualSize)
        return capture, videoWriter
        
    def read(self):
        """ Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: VideoStreamFrameException when no frame can be read
        """
        _, frame = self.stream.read()
        if frame is not None:
            self.currentFrameIdx +=1
            return Frame(frame.astype(np.float32))
        else:
            raise VideoStreamFrameException("UsbVideoStream frame not found")
            
    def stopRecording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to print upon closing.
        """
        self.stream.release()
        VideoStream.stopRecording(self, msg)
        self.currentFrameIdx=-1

class PiVideoStream(VideoStream):
    """
    A subclass of VideoStream for the raspberryPi camera
    which isn't supported by opencv
    """
    def __init__(self, savePath, bgStart, nBackgroundFrames):
        """
        :param str filePath: The destination file path to save the video to
        :param int bgStart: The frame to use as background frames range start
        :param int nBackgroundFrames: The number of frames to use for the background
        """
        VideoStream.__init__(self, savePath, bgStart, nBackgroundFrames)

    def _init_cam(self):
        """
        Initialises the CvPiCamera object to provide the frames
        """
        self._cam = CvPiCamera()
        self._cam.resolution = FRAME_SIZE[::-1] # openCV flips dimensions
        if os.getuid() == 0:
            self._cam.led = False
        else:
            print("LED kept on. To turn off run as root")
        
    def _startVideoCaptureSession(self, savePath):
        """
        Initiates a picamera.array.PiRGBArray object to store
        the frames from the picamera when reading 
        and a cv2.VideoWriter object to save a potential output
        
        :param str filePath: the destination file path
        
        :return: array and videoWriter object
        :type: (picamera.array.PiRGBArray, cv2.VideoWriter)
        """
        videoWriter = cv2.VideoWriter(savePath, CODEC, FPS, FRAME_SIZE)
        stream = picamera.array.PiRGBArray(self._cam)
        return stream, videoWriter
        
    def read(self):
        """
        Returns the next frame after updating the count
        
        :return: A video frame
        :rtype: video_frame.Frame
        """
        stream = self.stream
        self._cam.quickCapture(stream)
        # stream.array now contains the image data in BGR order
        frame = stream.array
        stream.truncate(0)
        self.currentFrameIdx +=1
        return Frame(frame.astype(np.float32))
        
    def restartRecording(self, reset):
        """
        Restarts the camera and potentially resets the output stream and frame index
        
        :param bool reset: Whether to reset the output stream (overwrite previous) and frame index
        """
        if self._cam.closed:
            self._init_cam()
        if reset:
            self.stream, self.videoWriter = self._startVideoCaptureSession(self.savePath)
            self.currentFrameIdx = -1
    
    def stopRecording(self, msg):
        """
        Stops recording and performs cleanup actions
        
        :param str msg: The message to print before closing.
        """
        VideoStream.stopRecording(self, msg)
        self._cam.closeEncoder()
        self._cam.close()
        
class VideoStreamFrameException(Exception):
    """
    A VideoStream specific exception meant to be raised
    if some recoverable frame error occurs
    (e.g. Skipped frame)
    """
    pass
    
class VideoStreamIOException(Exception):
    """
    A VideoStream specific exception meant to be raised
    if some i/o problem occurs with the stream
    (e.g. bad cam or unreadable video)
    """
    pass

class VideoStreamTypeException(Exception):
    """
    A VideoStream specific exception meant to be raised
    if some type problem occurs with the stream
    (e.g. bad input format)
    Especially useful to check since openCV error messages
    not specific
    """
    pass
    
class QuickRecordedVideoStream(RecordedVideoStream):
    """
    A subclass of RecordedVideoStream that supplies the frames from a
    video file but allows seeking (downscales the video (* 0.2) and loads everything in a numpy array.
    """
    def __init__(self, filePath, bgStart, nBackgroundFrames):
        """
        :param str filePath: The source file path to read for the video
        :param int bgStart: The frame to use as background frames range start
        :param int nBackgroundFrames: The number of frames to use for the background
        """
        self.nFrames = self._getNFrames(cv2.VideoCapture(filePath))
        self.size = self.frames[0].shape[:2]
        VideoStream.__init__(self, filePath, bgStart, nBackgroundFrames)
        self.fourcc = int(self.stream.get(cv.CV_CAP_PROP_FOURCC))
        self.fps = self._getFps()
        self.duration = self.nFrames / float(self.fps)
        
    def _getNFrames(self, stream):
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
        nFrames = 0
        self.frames = []
        while True:
            gotFrame, frame = stream.read()
            if gotFrame:
                nFrames +=1
                frame = scipy.misc.imresize(frame, 0.2, interp='bilinear')
                self.frames.append(frame)
            else:
                break
        if nFrames == 0:
            raise VideoStreamIOException("Could not read video")
        else:
            return nFrames
    
    def read(self, idx=None):
        """
        Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: EOFError when end of stream is reached
        """
        if idx is None:
            self.currentFrameIdx += 1
        else:
            self.currentFrameIdx = idx
        if self.currentFrameIdx > self.nFrames:
            raise EOFError("End of recording reached")
        frame = self.frames[self.currentFrameIdx]
        return Frame(frame)
