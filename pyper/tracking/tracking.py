# -*- coding: utf-8 -*-
"""
*******************
The tracking module
*******************

IT is the main module after the interface.
This module used inspiration from code developed by Antonio Gonzalez for the trackFrame function

If running on an ARM processor, it assumes the platform is a Raspberry Pi and thus uses the pi camera
instead of a usb camera by default. It also slightly optimises for speed.
:author: crousse
"""
from __future__ import division

import platform

import numpy as np
import cv2
from progressbar import *

from time import time

from pyper.contours.object_contour import ObjectContour
from pyper.video.video_frame import Frame
from pyper.video.video_stream import PiVideoStream, UsbVideoStream, RecordedVideoStream, VideoStreamFrameException
from pyper.contours.roi import Circle

isPi = (platform.machine()).startswith('arm')  # We assume all ARM is a raspberry pi

class Viewer(object):
    """
    A viewer class, a form of simplified Tracker for display purposes
    It can be used to retrieve some parameters of the video or just display
    """
    def __init__(self, srcFilePath=None, bgStart=0, nBackgroundFrames=1, delay=5):
        """
        :param str srcFilePath: The source file path to read from (camera if None)
        :param int bgStart: The frame to use as first background frame
        :param int nBackgroundFrames: The number of frames to use for the background\
        A number >1 means average
        :param int delay: The time in ms to wait between frames
        """
        trackRangeParams = (bgStart, nBackgroundFrames)
        if srcFilePath is None:
            if isPi:
                self._stream = PiVideoStream(destFilePath, *trackRangeParams)
            else:
                self._stream = UsbVideoStream(destFilePath, *trackRangeParams)
        else:
            self._stream = RecordedVideoStream(srcFilePath, *trackRangeParams)
        self.delay = delay
        
    def view(self):
        """
        Displays the recording to the user and returns 3 variables
        bgFrame, trackStart, trackEnd that are set using the keys
        'b', 's', and 'e' respectively
        The user can stop by pressing 'q'
        
        :return: (bgFrame, trackStart, trackEnd)
        :rtype: (int, int, int)
        """
        isRecording = hasattr(self._stream, 'nFrames')
        if isRecording:
            widgets=['Video Progress: ', Percentage(), Bar()]
            pbar = ProgressBar(widgets=widgets, maxval=self._stream.nFrames).start()
        bgFrame = trackStart = trackEnd = None
        while True:
            try:
                frame = self._stream.read()
                frameId = self._stream.currentFrameIdx
                if frame.shape[2] == 1:
                    frame = np.dstack([frame]*3)
                if not frame.dtype == np.uint8:
                    frame = frame.astype(np.uint8)
                frame = frame.copy()
                kbdCode = frame.display(win_name='Frame', text='Frame: {}'.format(frameId), delay=self.delay, get_code=True)
                kbdCode = kbdCode if kbdCode==-1 else chr(kbdCode & 255)
                if kbdCode == 'b': bgFrame = frameId
                elif kbdCode == 's': trackStart = frameId
                elif kbdCode == 'e': trackEnd = frameId
                elif kbdCode == 'q':
                    break
                    
                if (bgFrame is not None) and (trackStart is not None) and (trackEnd is not None):
                    break
                if isRecording: pbar.update(frameId)
            except VideoStreamFrameException: pass
            except (KeyboardInterrupt, EOFError) as e:
                if isRecording: pbar.finish()
                msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
                self._stream.stopRecording(msg)
                break
        if trackEnd is None:
            trackEnd = self._stream.currentFrameIdx
        if bgFrame is None:
            bgFrame = 0
        if __debug__:
            print(bgFrame, trackStart, trackEnd)
        return (bgFrame, trackStart, trackEnd)
        
    def timeStrToFrameIdx(self, timeStr):
        """
        Returns the frame number that corresponds to that time.
        
        :param str timeStr: A string of the form 'mm:ss'
        :return Idx: The corresponding frame index
        :rtype: int
        """
        return self._stream.timeStrToFrameIdx(timeStr)

class Tracker(object):
    """
    A tracker object to track a mouse in a video stream
    """
    def __init__(self, srcFilePath=None, destFilePath=None, 
                threshold=20, minArea=100, maxArea=5000,
                teleportationThreshold=10,
                bgStart=0, trackFrom=1, trackTo=None,
                nBackgroundFrames=1, nSds=5.0,
                clearBorders=False, normalise=False,
                plot=False, fast=False, extractArena=False,
                cameraCalibration=None,
                callback=None):
        """
        :param str srcFilePath: The source file path to read from (camera if None)
        :param str destFilePath: The destinatiopn file path to save the video
        :param int threshold: The numeric threshold for the masks (0<t<256)
        :param int minArea: The minimum area in pixels to be considered a valid mouse
        :param int minArea: The maximum area in pixels to be considered a valid mouse
        :param teleportationThreshold: The maximum number of pixels the mouse can \
        move in either dimesion (x,y) between 2 frames.
        :param int bgStart: The frame to use as first background frame
        :param int nBackgroundFrames: The number of frames to use for the background\
        A number >1 means average
        :param int nSds: The number of standard deviations the signal has to be above\
        to be considered above threshold. This option is not used if \
        nBackgroundFrames < 2
        :param int trackFrom: The frame to start tracking from
        :param int trackTo: The frame to stop tracking at
        :param bool clearBorders: Whether to clear objects that touch the outer borders\
        of the image.
        :param bool normalise: TODO
        :param bool plot: Whether to display the data during tracking:
        :param bool fast: Whether to skip some processing (e.g. frame denoising) for \
        the sake of acquisition speed.
        :param bool extractArena: Whether to detect the arena (it should be brighter than\
        the surrounding) from the background as an ROI.
        :param callback: The function to be executed upon finding the mouse in the ROI \
        during tracking.
        :type callback: `function`
        """

        if callback is not None: self.callback = callback
        trackRangeParams = (bgStart, nBackgroundFrames)
        if srcFilePath is None:
            if isPi:
                self._stream = PiVideoStream(destFilePath, *trackRangeParams)
            else:
                self._stream = UsbVideoStream(destFilePath, *trackRangeParams)
        else:
            self._stream = RecordedVideoStream(srcFilePath, *trackRangeParams)
        
        self.threshold = threshold
        self.minArea = minArea
        self.maxArea = maxArea
        self.teleportationThreshold = teleportationThreshold
        
        self.trackFrom = trackFrom
        self.trackTo = trackTo
        
        self.clearBorders = clearBorders
        self.normalise = normalise
        self.plot = plot
        self.fast = fast
        self.extractArena = extractArena
        
        self.nSds = nSds
        self.bg = None
        self.bgStd = None
        
        self.cameraCalibration = cameraCalibration
        
        self.defaultPos = (-1, -1)
        self.positions = []
        
    def _extractArena(self):
        """
        Finds the arena in the current background frame and
        converts it to an roi object.
        
        :return: arena
        :rtype: Circle
        """
        bg = self.bg.copy()
        bg = bg.astype(np.uint8)
        mask = bg.threshold(self.threshold)
        cnt = self._getBiggestContour(mask)
        arena = Circle(*cv2.minEnclosingCircle(cnt))
        self.distancesFromArena = []
        return arena
        
    def _makeBottomSquare(self):
        """
        Creates a set of diagonaly opposed points to use as the corners
        of the square displayed by the default callback method.
        """
        bottomRightPt = self._stream.size
        topLeftPt = tuple([p-50 for p in bottomRightPt])
        self.bottomSquare = (topLeftPt, bottomRightPt)
        
    def track(self, roi=None, checkFps=False, record=False, reset=True):
        """
        | The main function.
        | Loops until the end of the recording (ctrl+c if acquiring).
        
        :param roi: optional roi e.g. Circle((250, 350), 25)
        :type roi: roi subclass
        :param bool checkFps: Whether to print the current frame per second processing speed
        :param bool record: Whether to save the frames being processed
        :param bool reset: whether to reset the recording (restart the background and arena ...).\
        If this parameter is False, the recording will continue from the previous frame.
        
        :returns: the list of positions
        :rtype: list
        """
        self.roi = roi
        if roi is not None:
            self._makeBottomSquare()
        
        isRecording = type(self._stream) == RecordedVideoStream
        self.bg = None # reset for each track
        if isRecording:
            widgets=['Tracking frames: ', Percentage(), Bar()]
            pbar = ProgressBar(widgets=widgets, maxval=self._stream.nFrames).start()
        elif isPi:
            self._stream.restartRecording(reset)

        if checkFps: prevTime = time()
        while True:
            try:
                if checkFps: prevTime = self._checkFps(prevTime)
                frame = self._stream.read()
                if self.cameraCalibration is not None:
                    frame = self.cameraCalibration.remap(frame)
                fid = self._stream.currentFrameIdx
                if self.trackTo and (fid > self.trackTo):
                    raise KeyboardInterrupt # stop recording
                    
                if fid < self._stream.bgStartFrame:
                    continue # Skip junk frames
                elif self._stream.isBgFrame():
                    self._buildBg(frame)
                elif self._stream.bgEndFrame < fid < self.trackFrom:
                    continue # Skip junk frames
                else: # Tracked frame
                    if fid == self.trackFrom: self._finaliseBg()
                    sil = self._trackFrame(frame)
                    if sil is None:
                        continue # Skip if no contour found
                    else:
                        self.silhouette = sil.copy()
                    if self.roi is not None: self._checkMouseInRoi()
                    if self.plot: self._plot()
                    if record: self._stream._save(self.silhouette)
                if isRecording: pbar.update(self._stream.currentFrameIdx)
            except VideoStreamFrameException as e:
                print('Error with video_stream at frame {}: \n{}'.format(fid, e))
            except (KeyboardInterrupt, EOFError) as e:
                if isRecording: pbar.finish()
                msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
                self._stream.stopRecording(msg)
                return self.positions
                
    def _lastPosIsDefault(self):
        lastPos = tuple(self.positions[-1])
        if lastPos == self.defaultPos:
            return True
        else:
            return False

    def _checkMouseInRoi(self):
        """
        Checks whether the mouse is within the specified ROI and
        calls the specified callback method if so.
        """
        if self._lastPosIsDefault():
            return
        if self.roi.pointInRoi(self.positions[-1]):
            self.callback()
            self.silhouette = self.silhouette.copy()
            
    def _getDistanceFromArenaBorder(self):
        if self._lastPosIsDefault():
            return
        if self.extractArena:
            lastPos = tuple(self.positions[-1])
            return self.arena.distFromBorder(lastPos)
            
    def _getDistanceFromArenaCenter(self):
        if self._lastPosIsDefault():
            return
        if self.extractArena:
            lastPos = tuple(self.positions[-1])
            return self.arena.distFromCenter(lastPos)
            
    def paint(self, frame, roiColor='y', arenaColor='m'):
        if self.roi is not None:
            roiContour = ObjectContour(self.roi.points, frame, contourType='raw', color=roiColor, lineThickness=2)
            roiContour.draw()
        if self.extractArena:
            arenaContour = ObjectContour(self.arena.points, frame, contourType='raw', color=arenaColor, lineThickness=2)
            arenaContour.draw()

    def _plot(self):
        """
        Displays the current frame with the mouse trajectory and potentially the ROI and the
        Arena ROI if these have been specified.
        """
        sil = self.silhouette
        self.paint(sil)
        sil.display(win_name='Diff', text='Frame: {}'.format(self._stream.currentFrameIdx), curve=self.positions)

    def callback(self):
        """
        The method called when the mouse is found in the roi.
        This method is meant to be overwritten in subclasses of Tracker.
        """
        cv2.rectangle(self.silhouette, self.bottomSquare[0], self.bottomSquare[1], (0, 255, 255), -1)

    def _buildBg(self, frame):
        """
        Initialise the background if empty, expand otherwise.
        Will also initialise the arena roi if the option is selected
        
        :param frame: The video frame to use as background or part of the background.
        :type frame: video_frame.Frame
        """
        if __debug__:
            print("Building background")
        bg = frame.denoise().blur().gray()
        if self.bg is None:
            self.bg = bg
        else:
            self.bg = Frame(np.dstack((self.bg, bg)))
        if self.extractArena:
            self.arena = self._extractArena()
                
    def _finaliseBg(self):
        """
        Finalise the background (average stack and compute SD if more than one image)
        """
        if self.bg.ndim > 2:
            self.bgStd = np.std(self.bg, axis=2)
            self.bg = np.average(self.bg, axis=2)
        if self.normalise:
            self.bgAvgAvg = self.bg.mean()# TODO: rename
    
    def _trackFrame(self, frame, requestedColor='r', requestedOutput='raw'):
        """
        Get the position of the mouse in frame and append to self.positions
        Returns the mask of the current frame with the mouse potentially drawn
        
        :param frame: The video frame to use.
        :type: video_frame.Frame
        :param str requestedColor: A character (for list of supported charaters see ObjectContour) idicating the color to draw the contour
        :param str requestedOutput: Which frame type to output (one of ['raw', 'mask', 'diff'])
        :returns: silhouette
        :rtype: binary mask or None
        """
        treatedFrame = frame.gray()
        fast = self.fast
        if not isPi and not fast:
            treatedFrame = treatedFrame.denoise().blur()
        silhouette, diff = self._getSilhouette(treatedFrame)
        
        biggestContour = self._getBiggestContour(silhouette)
        
        plotSilhouette = None
        if fast:
            requestedOutput = 'mask'
        self.positions.append(self.defaultPos)
        if biggestContour is not None:
            area = cv2.contourArea(biggestContour)
            if self.minArea < area < self.maxArea:
                if self.plot:
                    if requestedOutput == 'raw':
                        plotSilhouette = (frame.color()).copy()
                        color = requestedColor
                    elif requestedOutput == 'mask':
                        plotSilhouette = silhouette.copy()
                        color = 'w'
                    elif requestedOutput == 'diff':
                        plotSilhouette = (diff.color()).copy()
                        color = requestedColor
                    else:
                        raise NotImplementedError("Expected one of ['raw', 'mask', 'diff'] for requestedOutput, got: {}".format(requestedOutput))
                else:
                    color = 'w'
                mouse = ObjectContour(biggestContour, plotSilhouette, contourType='raw', color=color)
                if plotSilhouette is not None:
                    mouse.draw()
                self.positions[-1] = mouse.centre
            else:
                if area > self.maxArea:
                    if not fast:
                        print('Frame: {}, found something too big in the arena ({} > {})'.format(
                        self._stream.currentFrameIdx, area, self.maxArea))
                else:
                    if not fast:
                        print('Frame: {}, biggest structure too small ({} < {})'.format(
                        self._stream.currentFrameIdx, area, self.minArea))
                return None
        else:
            print('Frame {}, no contour found'.format(self._stream.currentFrameIdx))
            return None
        self._checkTeleportation(frame, silhouette)
        return plotSilhouette if plotSilhouette is not None else silhouette
        
    def _checkFps(self, prevTime):
        """
        Prints the number of frames per second
        using the time elapsed since prevTime.
        
        :param prevTime: 
        :type prevTime: time object
        :returns: The new time
        :rtype: time object
        """
        fps = 1/(time()-prevTime)
        print("{} fps".format(fps))
        return time()
        
    def _checkTeleportation(self, frame, silhouette):
        """
        Check if the mouse moved too much, which would indicate an issue with the tracking
        notably the fitting in the past. If so, call self._stream.stopRecording() and raise
        EOFError.
        
        :param frame: The current frame (to be saved for troubleshooting if teleportation occured)
        :type frame: video_frame.Frame
        :param silhouette: The binary mask of the current frame (to be saved for troubleshooting if teleportation occured)
        :type silhouette: video_frame.Frame
        
        :raises: EOFError if the mouse teleported
        """
        if len(self.positions) < 2:
            return
        lastVector = np.abs(np.array(self.positions[-1]) - np.array(self.positions[-2]))
        if (lastVector > self.teleportationThreshold).any():
            silhouette.save('teleportingSilhouette.tif')
            frame.save('teleportingFrame.tif')
            errMsg = 'Frame: {}, mouse teleported from {} to {}'.format(self._stream.currentFrameIdx, *self.positions[-2:])
            errMsg += '\nPlease see teleportingSilhouette.tif and teleportingFrame.tif for debuging'
            self._stream.stopRecording(errMsg)
            raise EOFError('End of recording reached')
            
    def _getBiggestContour(self, silhouette):
        """
        We need to rerun if too many contours are found as it should means
        that the findContours function returned nonsense.
        
        :param silhouette: The binary mask in which to find the contours
        :type silhouette: video_frame.Frame
        
        :return: The contours and the biggest contour from the mask (None, None) if no contour found
        """
        contours, hierarchy = cv2.findContours(np.copy(silhouette),
                                                mode=cv2.RETR_LIST, 
                                                method=cv2.CHAIN_APPROX_NONE) # TODO: check if CHAIN_APPROX_SIMPLE better
        if contours:
            idx = np.argmax([cv2.contourArea(c) for c in contours])
            return contours[idx]
        
    def _getSilhouette(self, frame):
        """
        Get the binary mask (8bits) of the mouse 
        from the thresholded difference between frame and the background
        
        :param frame: The current frame to analyse
        :type frame: video_frame.Frame
        
        :returns: silhouette (the binary mask)
        :rtype: video_frame.Frame
        """
        if self.normalise:
            frame = frame.normalise(self.bgAvgAvg)
        diff = Frame(cv2.absdiff(frame, self.bg))
        if self.bgStd is not None:
            threshold = self.bgStd * self.nSds
            silhouette = diff > threshold
            silhouette = silhouette.astype(np.uint8) * 255
        else:
            diff = diff.astype(np.uint8)
            silhouette = diff.threshold(self.threshold)
        if self.clearBorders:
            silhouette.clearBorders()
        return silhouette, diff

class GuiTracker(Tracker):
    """
    A subclass of Tracker that reimplements trackFrame for use with the GUI
    This class implements read() to behave as a stream
    """
    def __init__(self, uiIface, srcFilePath=None, destFilePath=None, 
                threshold=20, minArea=100, maxArea=5000,
                teleportationThreshold=10,
                bgStart=0, trackFrom=1, trackTo=None,
                nBackgroundFrames=1, nSds=5.0,
                clearBorders=False, normalise=False,
                plot=False, fast=False, extractArena=False,
                cameraCalibration=None,
                callback=None):
        """
        :param TrackerInterface uiIface: the interface this tracker is called from
        
        For the other parameters, see Tracker
        """
        Tracker.__init__(self, srcFilePath=srcFilePath, destFilePath=destFilePath, 
                        threshold=threshold, minArea=minArea, maxArea=maxArea,
                        teleportationThreshold=teleportationThreshold,
                        bgStart=bgStart, trackFrom=trackFrom, trackTo=trackTo,
                        nBackgroundFrames=nBackgroundFrames, nSds=nSds,
                        clearBorders=clearBorders, normalise=normalise,
                        plot=plot, fast=fast, extractArena=extractArena,
                        cameraCalibration=cameraCalibration,
                        callback=callback)
        self.uiIface = uiIface
        self.currentFrameIdx = 0
        self.record = destFilePath is not None
    
    def setRoi(self, roi):
        """
        Set the region of interest and enable it
        """
        self.roi = roi
        if roi is not None:
            self._makeBottomSquare()

    def read(self):
        """
        The required method to behave as a video stream
        It calls self.track() and increments the currentFrameIdx
        It also updates the uiIface positions accordingly
        """
        try:
            self.currentFrameIdx = self._stream.currentFrameIdx + 1
            result = self.trackFrame(record=self.record, requestedOutput=self.uiIface.outputType)
        except EOFError:
            self.uiIface._stop('End of recording reached')
            return
        except cv2.error as e:
            self.uiIface.timer.stop()
            self._stream.stopRecording('Error {} stopped recording'.format(e))
            return
        if result is not None:
            img, position, distances = result
            self.uiIface.positions.append(position)
            self.uiIface.distancesFromArena.append(distances)
            return img
        else:
            self.uiIface.positions.append(self.defaultPos)
            self.uiIface.distancesFromArena.append(self.defaultPos)
    
    def trackFrame(self, record=False, requestedOutput='raw'):
        """
        Reimplementation of Tracker.trackFrame for the GUI
        """
        try:
            frame = self._stream.read()
            if self.cameraCalibration is not None:
                frame = Frame(self.cameraCalibration.remap(frame))
            fid = self._stream.currentFrameIdx
            if self.trackTo and (fid > self.trackTo):
                raise KeyboardInterrupt # stop recording
                
            if fid < self._stream.bgStartFrame:
                return frame.color(), self.defaultPos, self.defaultPos # Skip junk frames
            elif self._stream.isBgFrame():
                self._buildBg(frame)
                if record: self._stream._save(frame)
                return frame.color(), self.defaultPos, self.defaultPos
            elif self._stream.bgEndFrame < fid < self.trackFrom:
                if record: self._stream._save(frame)
                return frame.color(), self.defaultPos, self.defaultPos # Skip junk frames
            else: # Tracked frame
                if fid == self.trackFrom: self._finaliseBg()
                sil = self._trackFrame(frame, 'b', requestedOutput=requestedOutput)
                if sil is None:
                    if record: self._stream._save(frame)
                    return None, self.defaultPos, self.defaultPos # Skip if no contour found
                else:
                    self.silhouette = sil.copy()
                if self.roi is not None: self._checkMouseInRoi()
                self.paint(self.silhouette, 'c')
                self.silhouette.paint(curve=self.positions)
                if record: self._stream._save(self.silhouette)
                result = [self.silhouette, self.positions[-1]]
                if self.extractArena:
                    distances = (self._getDistanceFromArenaCenter(), self._getDistanceFromArenaBorder())
                    self.distancesFromArena.append(distances)
                    result.append(self.distancesFromArena[-1])
                else:
                    result.append(self.defaultPos)
                return result
        except VideoStreamFrameException as e:
            print('Error with video_stream at frame {}: \n{}'.format(fid, e))
        except (KeyboardInterrupt, EOFError) as e:
            msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
            self._stream.stopRecording(msg)
            raise EOFError
