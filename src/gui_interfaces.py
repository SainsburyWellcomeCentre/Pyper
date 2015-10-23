# -*- coding: utf-8 -*-
"""
*************************
The gui_interfaces module
*************************

Creates the class links to allow the graphical interface.
It essentially implements a class for each graphical interface tab.

:author: crousse
"""

import sys, os, csv

import cv2

import numpy as np
from scipy.misc import imsave
import matplotlib
matplotlib.use('qt5agg') # For OSX otherwise, the default backed doesn't allow to draw to buffer
from matplotlib import pyplot as plt

from PyQt5.QtWidgets import QFileDialog

from PyQt5.QtCore import QObject, pyqtSlot, QVariant, QTimer

from PyQt5.QtCore import Qt

from tracking import GuiTracker
from video_stream import QuickRecordedVideoStream as VStream
from video_stream import ImageListVideoStream
from roi import Circle
import video_analysis
from camera_calibration import CameraCalibration
from image_providers import CvImageProvider, PyplotImageProvider

VIDEO_FILTERS = "Videos (*.h264 *.avi *.mpg)"

class BaseInterface(QObject):
    """
    Abstract interface
    This class is meant to be subclassed by the other classes of the module
    PlayerInterface, TrackerIface (base themselves to ViewerIface, CalibrationIface, RecorderIface)
    It supplies the base methods and attributes to register an object with video in qml.
    It also possesses an instance of ParamsIface to 
    """
    def __init__(self, app, context, parent, params, displayName, providerName, timerSpeed=20):
        QObject.__init__(self, parent)
        self.app = app # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.ctx = context
        self.win = parent
        self.displayName = displayName
        self.providerName = providerName
        self.params = params
        
        self.timer = QTimer(self)
        self.timerSpeed = timerSpeed
        self.timer.timeout.connect(self.getImg)

    def getImg(self):
        """
        The method called by self.timer to play the video
        """
        if self.stream.currentFrameIdx < self.nFrames and self.stream.currentFrameIdx >= -1:
            try:
                self.display.reload()
                self._updateDisplayIdx()
            except EOFError:
                self.timer.stop()
        else:
            self.timer.stop()

    def _setDisplay(self):
        """
        Gets the display from the qml code
        
        :param string displayName: The exact name of the display in the qml code
        """
        self.display = self.win.findChild(QObject, self.displayName)

    def _updateDisplayIdx(self):
        """
        Updates the value of the display progress bar
        """
        self.display.setProperty('value', self.stream.currentFrameIdx)
        
    def _setDisplayMax(self):
        """
        Sets the maximum of the display progress bar
        """
        self.display.setProperty('maximumValue', self.nFrames)
    
    @pyqtSlot(result=QVariant)
    def getFrameIdx(self):
        """
        pyQT slot to return the index of the currently displayed frame
        """
        return str(self.stream.currentFrameIdx)
        
    @pyqtSlot(result=QVariant)
    def getNFrames(self):
        """
        pyQT slot to return the number of frames of the current display
        """
        return self.nFrames
        
    def _updateImgProvider(self):
        """
        Registers the objects image provider with the qml code
        Based on self.providerName
        """
        engine = self.ctx.engine()
        self.imageProvider = CvImageProvider(requestedImType='pixmap', stream=self.stream)
        engine.addImageProvider(self.providerName, self.imageProvider)
    
class PlayerInterface(BaseInterface):
    """
    This (abstract) class extends the BaseInterface to allow controlable videos (play, pause, forward...)
    """
    @pyqtSlot()
    def play(self):
        """
        Start video (timer) playback
        """
        self.timer.start(self.timerSpeed)

    @pyqtSlot()
    def pause(self):
        """
        Pause video (timer) playback
        """
        self.timer.stop()

    @pyqtSlot(QVariant)
    def move(self, stepSize):
        """
        Moves in the video by stepSize
        
        :param int stepSize: The number of frames to scroll by (positive or negative)
        """
        targetFrame = self.stream.currentFrameIdx
        targetFrame -= 1 # reset
        targetFrame += int(stepSize)
        self.stream.currentFrameIdx = self._validateFrameIdx(targetFrame)
        self.getImg()

    @pyqtSlot(QVariant)
    def seekTo(self, frameIdx):
        """
        Seeks directly to frameIdx in the video
        
        :param int frameIdx: The frame to get to
        """
        self.stream.currentFrameIdx = self._validateFrameIdx(frameIdx)
        self.getImg()
    
    def _validateFrameIdx(self, frameIdx):
        """
        Checks if the supplied frameIdx is within [0:nFrames]

        :returns: A bound index
        :rtype: int
        """
        if frameIdx >= self.nFrames:
            frameIdx = self.nFrames - 1
        elif frameIdx < 0:
            frameIdx = 0
        return frameIdx

class ViewerIface(PlayerInterface):
    """
    Implements the PlayerInterface class with a QuickRecordedVideoStream
    It is meant for video preview with frame precision seek
    """
    
    @pyqtSlot()
    def load(self):
        """
        Loads the video into memory
        """
        self.stream = VStream(self.params.srcPath, 0, 1)
        self.nFrames = self.stream.nFrames - 1
        
        self._setDisplay()
        self._setDisplayMax()
        self._updateImgProvider()

class CalibrationIface(PlayerInterface):
    """
    Implements the PlayerInterface class with an ImageListVideoStream
    It uses the CameraCalibration class to compute the camera matrix from a set of images containing a
    chessboard pattern.
    """
    def __init__(self, app, context, parent, params, displayName, providerName, timerSpeed=200):
        PlayerInterface.__init__(self, app, context, parent, params, displayName, providerName, timerSpeed)
        
        self.nColumns = 9
        self.nRows = 6
        self.matrixType = 'normal'
        
        self._setDisplay()
        self._setDisplay()

    @pyqtSlot()
    def calibrate(self):
        """
        Compute the camera matrix 
        """
        self.calib = CameraCalibration(self.nColumns, self.nRows)
        self.calib.calibrate(self.srcFolder)
        self.params.calib = self.calib
        
        self.nFrames = len(self.calib.srcImgs)
        
        self.stream = ImageListVideoStream(self.calib.srcImgs)
        self._setDisplay()
        self._setDisplayMax()
        
        self._updateImgProvider()

    @pyqtSlot(result=QVariant)
    def getNRows(self):
        """
        Get the number of inner rows in the chessboard pattern
        """
        return self.nRows

    @pyqtSlot(QVariant)
    def setNRows(self, nRows):
        """
        Set the number of inner rows in the chessboard pattern
        """
        self.nRows = int(nRows)

    @pyqtSlot(result=QVariant)
    def getNColumns(self):
        """
        Get the number of inner columns in the chessboard pattern
        """
        return self.nColumns

    @pyqtSlot(QVariant)
    def setNColumns(self, nColumns):
        """
        Set the number of inner rows in the chessboard pattern
        """
        self.nColumns = int(nColumns)

    @pyqtSlot(result=QVariant)
    def getFolderPath(self):
        """
        Get the path to the folder where the images with the pattern are stored
        """
        diag = QFileDialog()
        srcFolder = diag.getExistingDirectory(parent=diag, caption="Chose directory",
                                            directory=os.getenv('HOME'))
        self.srcFolder = srcFolder
        return srcFolder

    @pyqtSlot(QVariant)
    def setMatrixType(self, matrixType):
        """
        Set the matrix type to be saved. Resolution independant (normal) or dependant (optimized)
        
        :param string matrixType: The type of matrix to be saved. One of ['normal', 'optimized']
        """
        matrixType = matrixType.lower()
        if matrixType not in ['normal', 'optimized']:
            raise KeyError("Expected one of ['normal', 'optimized'], got {}".format(matrixType))
        else:
            self.matrixType = matrixType

    @pyqtSlot()
    def saveCameraMatrix(self):
        """
        Save the camera matrix selected as self.matrixType
        """
        diag = QFileDialog()
        destPath = diag.getSaveFileName(parent=diag,
                                    caption='Save matrix',
                                    directory=os.getenv('HOME'), 
                                    filter='Numpy (.npy)')
        destPath = destPath[0]
        if destPath:
            if self.matrixType == 'normal':
                np.save(destPath, self.cameraMatrix)
            elif self.matrixType == 'optimized':
                np.save(destPath, self.optimalCameraMatrix)

    @pyqtSlot(QVariant)
    def setFrameType(self, frameType):
        """
        Selects the type of frame to be displayed. (Before, during or after distortion correction)
        
        :param string frameType: The selected frame type. One of ['source', 'detected', 'corrected']
        """
        frameType = frameType.lower()
        currentIndex = self.stream.currentFrameIdx
        if frameType == "source":
            imgs = self.calib.srcImgs
        elif frameType == "detected":
            imgs = self.calib.detectedImgs
        elif frameType == "corrected":
            imgs = self.calib.correctedImgs
        else:
            raise KeyError("Expected one of ['source', 'detected', 'corrected'], got {}".format(frameType))
        self.stream = ImageListVideoStream(imgs)
        self._updateImgProvider()
        self.stream.currentFrameIdx = self._validateFrameIdx(currentIndex -1) # reset to previous position
        self.getImg()

class TrackerIface(BaseInterface):
    """
    This class implements the BaseInterface to provide a qml interface
    to the GuiTracker object of the tracking module.
    """
    def __init__(self, app, context, parent, params, displayName, providerName):
        BaseInterface.__init__(self, app, context, parent, params, displayName, providerName)
        
        self.positions = []
        self.roi = None

    @pyqtSlot(QVariant, result=QVariant)
    def getRow(self, idx):
        """
        Get the data (position and distancesFromArena) at row idx
        
        :param int idx: The index of the row to return
        """
        idx = int(idx)
        if 0 <= idx < len(self.positions):
            row = [idx] + list(self.positions[idx]) + list(self.distancesFromArena[idx])
            return [str(e) for e in row]
        else:
            return -1

    @pyqtSlot()
    def load(self):
        """
        Load the video and create the GuiTracker object
        Also registers the analysis image providers (for the analysis tab) with QT
        """
        self.tracker = GuiTracker(self, srcFilePath=self.params.srcPath, destFilePath=None,
                                nBackgroundFrames=1, plot=True,
                                fast=False, cameraCalibration=self.params.calib,
                                callback=None)
        self.stream = self.tracker # To comply with BaseInterface
        self.tracker.roi = None

        self.nFrames = self.tracker._stream.nFrames - 1
        self.currentFrameIdx = self.tracker._stream.currentFrameIdx
        
        if self.params.endFrameIdx == -1:
            self.params.endFrameIdx = self.nFrames
        
        self._setDisplay()
        self._setDisplayMax()
        self._updateImgProvider()
        
        engine = self.ctx.engine()
        self.analysisImageProvider = PyplotImageProvider(fig=None)
        engine.addImageProvider("analysisprovider", self.analysisImageProvider)
        self.analysisImageProvider2 = PyplotImageProvider(fig=None)
        engine.addImageProvider("analysisprovider2", self.analysisImageProvider2)

    @pyqtSlot()
    def start(self):
        """
        Start the tracking of the loaded video with the parameters from self.params
        """
        self.positions = [] # reset between runs
        self.distancesFromArena = []
        
        self.tracker._stream.bgStartFrame = self.params.bgFrameIdx
        nBackgroundFrames = self.params.nBgFrames
        self.tracker._stream.bgEndFrame = self.params.bgFrameIdx + nBackgroundFrames - 1
        self.tracker.trackFrom = self.params.startFrameIdx
        self.tracker.trackTo = self.params.endFrameIdx if (self.params.endFrameIdx > 0) else None
        
        self.tracker.threshold = self.params.detectionThreshold
        self.tracker.minArea = self.params.objectsMinArea
        self.tracker.maxArea = self.params.objectsMaxArea
        self.tracker.teleportationThreshold = self.params.teleportationThreshold
        
        self.tracker.nSds = self.params.nSds
        self.tracker.clearBorders = self.params.clearBorders
        self.tracker.normalise = self.params.normalise
        self.tracker.extractArena = self.params.extractArena
        
        self.tracker.setRoi(self.roi)
            
        self.timer.start(self.timerSpeed)

    @pyqtSlot()
    def stop(self):
        """
        The qt slot to self._stop()
        """
        self._stop('Recording stopped manually')
        
    def _stop(self, msg):
        """
        Stops the tracking gracefully
        
        :param string msg: The message to print upon stoping
        """
        self.timer.stop()
        self.tracker._stream.stopRecording(msg)
        
    @pyqtSlot(QVariant, QVariant, QVariant, QVariant, QVariant)
    def setRoi(self, width, height, x, y, diameter):
        """
        Sets the ROI (in which to check for the specimen) from the one drawn in QT
        Scaling is applied to match the (resolution difference) between the representation 
        of the frames in the GUI (on which the user draws the ROI) and the internal representation
        used to compute the position of the specimen.
        
        :param width: The width of the image representation in the GUI
        :param height: The height of the image representation in the GUI
        :param x: The center of the roi in the first dimension
        :param y: The center of the roi in the second dimension
        :param diameter: The diameter of the ROI
        """
        if hasattr(self, 'tracker'):
            streamWidth, streamHeight = self.tracker._stream.size # flipped for openCV
            horizontalScalingFactor = streamWidth / width
            verticalScalingFactor = streamHeight / height
            
            radius = diameter / 2.0
            scaledX = (x + radius) * horizontalScalingFactor
            scaledY = (y + radius) * verticalScalingFactor
            scaledRadius = radius * horizontalScalingFactor
            
            self.roi = Circle((scaledX, scaledY), scaledRadius)

    @pyqtSlot()
    def save(self):
        """
        Save the data (positions and distancesFromArena) as a csv style file
        """
        diag = QFileDialog()
        destPath = diag.getSaveFileName(parent=diag,
                                    caption='Save file',
                                    directory=os.getenv('HOME'), 
                                    filter="Text (*.txt *.dat *.csv)")
        destPath = destPath[0]
        if destPath:
            self.write(destPath)
    
    def write(self, dest):
        """
        The method called by save() to write the csv file
        """
        with open(dest, 'w') as outFile:
            writer = csv.writer(outFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for fid, row in enumerate(self.positions):
                writer.writerow([fid]+list(row))

    @pyqtSlot(QVariant)
    def setFrameType(self, outputType):
        """
        Set the type of frame to display. (As source, difference with background or binary mask)
        
        :param string outputType: The type of frame to display. One of ['Raw', 'Diff', 'Mask']
        """
        self.outputType = outputType.lower()

    @pyqtSlot()
    def analyseAngles(self):
        """
        Compute and plot the angles between the segment Pn -> Pn+1 and Pn+1 -> Pn+2
        """
        fig, ax = plt.subplots()
        angles = video_analysis.getAngles(self.positions)
        video_analysis.plotAngles(angles, self.getSamplingFreq())
        self.analysisImageProvider._fig = fig

    @pyqtSlot()
    def analyseDistances(self):
        """
        Compute and plot the distances between the points Pn and Pn+1
        """
        fig, ax = plt.subplots()
        distances = video_analysis.posToDistances(self.positions)
        video_analysis.plotDistances(distances, self.getSamplingFreq())
        self.analysisImageProvider2._fig = fig

    @pyqtSlot()
    def saveAnglesFig(self):
        """
        Save the graph as a png or jpeg image
        """
        diag = QFileDialog()
        destPath = diag.getSaveFileName(parent=diag,
                                    caption='Save file',
                                    directory=os.getenv('HOME'), 
                                    filter="Image (*.png *.jpg)")
        destPath = destPath[0]
        if destPath:
            imsave(destPath, self.analysisImageProvider.getArray())

    def getSamplingFreq(self):
        return self.tracker._stream.fps

    def getImg(self):
        if self.tracker._stream.currentFrameIdx < self.nFrames:
            self.display.reload()
            self._updateDisplayIdx()
        else:
            self._stop('End of recording reached')

class RecorderIface(TrackerIface):
    """
    This class extends the TrackerIface to provide video acquisition and live detection (tracking).
    It uses openCV to run the camera and thus should work with any camera supported by openCV.
    It uses the first available USB/firewire camera unless the platform is a raspberry pi,
    in which case it will use the pi camera.
    """

    @pyqtSlot()
    def load(self): # TODO: check if worth keeping
        pass
        
    @pyqtSlot()
    def start(self):
        """
        Start the recording and tracking.
        """
        self.positions = [] # reset between runs
        self.distancesFromArena = []
        
        bgStart = self.params.bgFrameIdx
        nBackgroundFrames = self.params.nBgFrames
        trackFrom = self.params.startFrameIdx
        trackTo = self.params.endFrameIdx if (self.params.endFrameIdx > 0) else None
        
        threshold = self.params.detectionThreshold
        minArea = self.params.objectsMinArea
        maxArea = self.params.objectsMaxArea
        teleportationThreshold = self.params.teleportationThreshold
        
        nSds = self.params.nSds
        clearBorders = self.params.clearBorders
        normalise = self.params.normalise
        extractArena = self.params.extractArena
        
        self.tracker = GuiTracker(self, record=True, srcFilePath=None, destFilePath=self.params.destPath,
                                threshold=threshold, minArea=minArea, maxArea=maxArea,
                                teleportationThreshold=teleportationThreshold,
                                bgStart=bgStart, trackFrom=trackFrom, trackTo=trackTo,
                                nBackgroundFrames=nBackgroundFrames, nSds=nSds,
                                clearBorders=clearBorders, normalise=normalise,
                                plot=True, fast=False, extractArena=extractArena,
                                cameraCalibration=self.params.calib,
                                callback=None)
        self.stream = self.tracker # To comply with BaseInterface
        self._setDisplay()
        self._updateImgProvider()
        
        self.tracker.setRoi(self.roi)
        
        self.timer.start(self.timerSpeed)
        
    def getSamplingFreq(self):
        """
        Return the sampling frequency (note this is a maximum and can be limited by a slower CPU)
        """
        return 1.0 / (self.timerSpeed / 1000.0) # timer speed in ms
        
    @pyqtSlot(result=QVariant)
    def camDetected(self):
        """
        Check if a camera is available
        """
        cap = cv2.VideoCapture(0)
        detected = False
        if cap.isOpened():
            detected = True
        cap.release()
        return detected

    def getImg(self):
        self.display.reload()

class ParamsIface(QObject):
    """
    The QObject derived class that stores most of the parameters from the graphical interface
    for the other QT interfaces
    """
    def __init__(self, app, context, parent):
        """
        :param app: The QT application
        :param context:
        :param parent: the parent window
        """
        QObject.__init__(self, parent)
        self.app = app # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context
        self._setDefaults()
        
        self.calib = None

    def _setDefaults(self):
        """
        Reset the parameters to default.
        To customise the defaults, users should do this here.
        """
        self.bgFrameIdx = 5
        self.nBgFrames = 1
        self.startFrameIdx = self.bgFrameIdx + self.nBgFrames
        self.endFrameIdx = -1
        
        self.detectionThreshold = 50
        self.objectsMinArea = 100
        self.objectsMaxArea = 5000
        self.teleportationThreshold = 10000
        self.nSds = 5.0
        
        self.clearBorders = False
        self.normalise = False
        self.extractArena = False

    def __del__(self):
        """
        Reset the standard out on destruction
        """
        sys.stdout = sys.__stdout__

    @pyqtSlot()
    def chgCursor(self):
        self.app.setOverrideCursor(Qt.CursorShape(Qt.CrossCursor))

    @pyqtSlot()
    def restoreCursor(self):
        self.app.restoreOverrideCursor()
    
    # BOOLEAN OPTIONS
    @pyqtSlot(bool)
    def setClearBorders(self, status):
        self.clearBorders = bool(status)

    @pyqtSlot(result=bool)
    def getClearBorders(self):
        return self.clearBorders

    @pyqtSlot(bool)
    def setNormalise(self, status):
        self.normalise = bool(status)

    @pyqtSlot(result=bool)
    def getNormalise(self):
        return self.normalise

    @pyqtSlot(bool)
    def setExtractArena(self, status):
        self.extractArena = bool(status)

    @pyqtSlot(result=bool)
    def getExtractArena(self):
        return self.extractArena

    # DETECTION OPTIONS
    @pyqtSlot(result=QVariant)
    def getDetectionThreshold(self):
        return self.detectionThreshold

    @pyqtSlot(QVariant)
    def setDetectionThreshold(self, threshold):
        self.detectionThreshold = int(threshold)

    @pyqtSlot(result=QVariant)
    def getMinArea(self):
        return self.objectsMinArea

    @pyqtSlot(QVariant)
    def setMinArea(self, area):
        self.objectsMinArea = int(area)

    @pyqtSlot(result=QVariant)
    def getMaxArea(self):
        return self.objectsMaxArea

    @pyqtSlot(QVariant)
    def setMaxArea(self, area):
        self.objectsMaxArea = int(area)

    @pyqtSlot(result=QVariant)
    def getMaxMovement(self):
        return self.teleportationThreshold

    @pyqtSlot(QVariant)
    def setMaxMovement(self, movement):
        self.teleportationThreshold = int(movement)

    @pyqtSlot(result=QVariant)
    def getNSds(self):
        return self.nSds

    @pyqtSlot(QVariant)
    def setNSds(self, n):
        self.nSds = int(n)    

    # FRAME OPTIONS
    @pyqtSlot(QVariant)
    def setBgFrameIdx(self, idx):
        self.bgFrameIdx = int(idx)
    
    @pyqtSlot(result=QVariant)
    def getBgFrameIdx(self):
        return self.bgFrameIdx

    @pyqtSlot(QVariant)
    def setNBgFrames(self, n):
        self.nBgFrames = int(n)
    
    @pyqtSlot(result=QVariant)
    def getNBgFrames(self):
        return self.nBgFrames

    @pyqtSlot(QVariant)
    def setStartFrameIdx(self, idx):
        if idx >= (self.bgFrameIdx + self.nBgFrames):
            self.startFrameIdx = int(idx)
        else:
            self.startFrameIdx = self.bgFrameIdx + self.nBgFrames

    @pyqtSlot(result=QVariant)
    def getStartFrameIdx(self):
        return self.startFrameIdx

    @pyqtSlot(QVariant)
    def setEndFrameIdx(self, idx):
        self.endFrameIdx = int(idx)        

    @pyqtSlot(result=QVariant)
    def getEndFrameIdx(self):
        return self.endFrameIdx

    @pyqtSlot(result=QVariant)   
    def openVideo(self):
        """
        The QT dialog to select the video to be used for preview or tracking
        """
        diag = QFileDialog()
        path = diag.getOpenFileName(parent=diag,
                                    caption='Open file',
                                    directory=os.getenv('HOME'), 
                                    filter=VIDEO_FILTERS)
        srcPath = path[0]
        if srcPath:
            self.srcPath = srcPath
            self._setDefaults()
            return srcPath

    @pyqtSlot(result=QVariant)   
    def setSavePath(self):
        """
        The QT dialog to select the path to save the recorded video
        """
        diag = QFileDialog()
        path = diag.getSaveFileName(parent=diag,
                                    caption='Save file',
                                    directory=os.getenv('HOME'), 
                                    filter=VIDEO_FILTERS)
        destPath = path[0]
        if destPath:
            self.destPath = destPath
            return destPath

    @pyqtSlot(result=QVariant)
    def isPathSelected(self):
        return hasattr(self, "srcPath")

    @pyqtSlot(result=QVariant)
    def getPath(self):
        return self.srcPath if hasattr(self, "srcPath") else ""

    @pyqtSlot(result=QVariant)
    def getFileName(self):
        path = self.getPath()
        return os.path.basename(path) if path else ""
