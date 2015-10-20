# -*- coding: utf-8 -*-
"""
**************
The GUI module
**************

Creates the class links to allow the graphical interface

.. note:: This module depends on importing OpenGL.GL although it doens't uses it directly

:author: crousse
"""

import sys, os,  csv

import numpy as np
from scipy.misc import imsave
import matplotlib
matplotlib.use('qt5agg') # For OSX otherwise, the default backed doesn't allow to draw to buffer
from matplotlib import pyplot as plt

from OpenGL import GL # Hack necessary to get qtQuick working

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication, QFileDialog

from PyQt5.QtCore import QObject, pyqtSlot, QVariant
from PyQt5.QtCore import QUrl, QTimer, QSize

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtQuick import QQuickImageProvider

from video_stream import QuickRecordedVideoStream as VStream
from video_stream import VideoStreamFrameException
from video_frame import Frame
from tracking import Tracker
from roi import Circle
import video_analysis
from camera_calibration import CameraCalibration

import cv2

DEBUG = True

class Logger(QObject):
    
    def __init__(self, context, parent=None, logObjectName="log"):
        QObject.__init__(self, parent)
        self.win = parent
        self.ctx = context
        self.log = self.win.findChild(QObject, logObjectName)
    
    def write(self, text):
        if text:
            previousText = self.log.property('text')
            outputText = '{}\n>>>{}'.format(previousText, text)
            self.log.setProperty('text', outputText)    

class MainIface(QObject):
    def __init__(self, app, context, parent=None):
        QObject.__init__(self, parent)
        self.app = app # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context
        
        if not DEBUG:
            self.logger = Logger(self.ctx, self.win, "log")
            sys.stdout = self.logger
        self._setDefaults()

    def _setDefaults(self):
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
        sys.stdout = sys.__stdout__   
    
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
        diag = QFileDialog()
        path = diag.getOpenFileName(parent=diag,
                                    caption='Open file',
                                    directory=os.getenv('HOME'), 
                                    filter="Videos (*.h264 *.avi *.mpg)")
        srcPath = path[0]
        if srcPath:
            self.srcPath = srcPath
            self._setDefaults()
            return srcPath

    @pyqtSlot(result=QVariant)   
    def setSavePath(self):
        diag = QFileDialog()
        path = diag.getSaveFileName(parent=diag,
                                    caption='Save file',
                                    directory=os.getenv('HOME'), 
                                    filter="Videos (*.h264 *.avi *.mpg)")
        destPath = path[0]
        if destPath:
            self.destPath = destPath
            return destPath

    @pyqtSlot(result=QVariant)
    def isPathSelected(self):
        return hasattr(self, "srcPath")

    @pyqtSlot(result=QVariant)
    def getPath(self):
        if hasattr(self, "srcPath"):
            return self.srcPath
        else:
            return ""

    @pyqtSlot(result=QVariant)
    def getFileName(self):
        path = self.getPath()
        if path:
            return os.path.basename(path)
        else:
            return ""

class Viewer(QObject):
    
    def __init__(self, app, context, parent=None, main=None):
        QObject.__init__(self, parent)
        self.app = app # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context
        self.main = main
        
        self.timer = QTimer(self)
        self.timerSpeed = 20
        self.timer.timeout.connect(self.getImg)

    @pyqtSlot()
    def load(self):
        self.stream = VStream(self.main.srcPath, 0, 1)
        self.nFrames = self.stream.nFrames - 1
        
        self.preview = self.win.findChild(QObject, "preview")
        self.preview.setProperty('maximumValue', self.nFrames)

        self.imageProvider = CvImageProvider(requestedImType='pixmap', stream=self.stream)
        engine = self.ctx.engine()
        engine.addImageProvider("viewerprovider", self.imageProvider)

    def validateFrameIdx(self, frameIdx):
        if frameIdx >= self.nFrames:
            frameIdx = self.nFrames - 1
        elif frameIdx < 0:
            frameIdx = 0
        return frameIdx

    @pyqtSlot()
    def start(self):
        self.timer.start(self.timerSpeed)

    @pyqtSlot()
    def pause(self):
        self.timer.stop()

    @pyqtSlot(QVariant)
    def move(self, stepSize):
        targetFrame = self.stream.currentFrameIdx
        targetFrame -= 1 # reset
        targetFrame += int(stepSize)
        self.stream.currentFrameIdx = self.validateFrameIdx(targetFrame)
        self.getImg()

    @pyqtSlot(QVariant)
    def seekTo(self, frameIdx):
        self.stream.currentFrameIdx = self.validateFrameIdx(frameIdx)
        self.getImg()

    @pyqtSlot(result=QVariant)
    def getFrameIdx(self):
        return str(self.stream.currentFrameIdx)

    @pyqtSlot(result=QVariant)
    def getNFrames(self):
        return self.nFrames

    def getImg(self):
        if self.stream.currentFrameIdx < self.nFrames and self.stream.currentFrameIdx >= -1:
            self.preview.reload()
            self.preview.setProperty('value', self.stream.currentFrameIdx)
        else:
            self.timer.stop()

class GuiTracker(Tracker):
    
    def setRoi(self, roi):
        self.roi = roi
        self._makeBottomSquare()
        self.defaultPos = (-1, -1)
    
    def trackFrame(self, record=False, requestedOutput='raw'):
        try:
            frame = self._stream.read()
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
                sil = self._trackFrame(frame, 'b',  requestedOutput=requestedOutput)
                if sil is None:
                    if record: self._stream._save(frame)
                    return (None, None, None)# Skip if no contour found
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
        except VideoStreamFrameException: pass
        except (KeyboardInterrupt, EOFError) as e:
            msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
            self._stream.stopRecording(msg)

class CalibrationIface(QObject):
    def __init__(self, app, context, parent=None, main=None):
        QObject.__init__(self, parent)
        self.app = app # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context
        self.main = main
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.getImg)
        self.timerSpeed = 200
        
        self.nColumns = 9
        self.nRows = 6
        self.matrixType = 'normal'
        
        self.display = self.win.findChild(QObject, "calibrationDisplay")

    @pyqtSlot()
    def calibrate(self):
        calib = CameraCalibration(self.nColumns, self.nRows)
        results = calib.calibrate(self.srcFolder)
        cameraMatrix, optimalCameraMatrix, distortionCoeffs, srcImgs, imgs, correctedImgs = results
        self.cameraMatrix = cameraMatrix
        self.optimalCameraMatrix = optimalCameraMatrix
        self.distortionCoeffs = distortionCoeffs
        
        self.sourceImgs = srcImgs
        self.detectedImgs = imgs
        self.correctedImgs = correctedImgs
        
        self.nFrames = len(self.sourceImgs)
        
        self.stream = ImageListVideoStream(self.sourceImgs)
        self.display = self.win.findChild(QObject, "calibrationDisplay")
        self.display.setProperty('maximumValue', self.nFrames)
        
        self._updateImgProvider()

    def _updateImgProvider(self):
        engine = self.ctx.engine()
        self.imageProvider = CvImageProvider(requestedImType='pixmap', stream=self.stream)
        engine.addImageProvider("calibrationprovider", self.imageProvider)

    @pyqtSlot()
    def play(self):
        self.timer.start(self.timerSpeed)

    @pyqtSlot()
    def pause(self):
        self.timer.stop()

    @pyqtSlot(QVariant)
    def move(self, stepSize):
        targetFrame = self.stream.currentFrameIdx
        targetFrame -= 1 # reset
        targetFrame += int(stepSize)
        self.stream.currentFrameIdx = self.validateFrameIdx(targetFrame)
        self.getImg()

    @pyqtSlot(QVariant)
    def seekTo(self, frameIdx):
        self.stream.currentFrameIdx = self.validateFrameIdx(frameIdx)
        self.getImg()

    def validateFrameIdx(self, frameIdx):
        if frameIdx >= self.nFrames:
            frameIdx = self.nFrames - 1
        elif frameIdx < 0:
            frameIdx = 0
        return frameIdx

    @pyqtSlot(result=QVariant)
    def getNRows(self):
        return self.nRows

    @pyqtSlot(QVariant)
    def setNRows(self, nRows):
        self.nRows = int(nRows)

    @pyqtSlot(result=QVariant)
    def getNColumns(self):
        return self.nColumns

    @pyqtSlot(QVariant)
    def setNColumns(self, nColumns):
        self.nColumns = int(nColumns)

    @pyqtSlot(result=QVariant)
    def getFolderPath(self):
        diag = QFileDialog()
        srcFolder = diag.getExistingDirectory(parent=diag, caption="Chose directory",
                                            directory=os.getenv('HOME'))
        self.srcFolder = srcFolder
        return srcFolder

    @pyqtSlot(QVariant)
    def setMatrixType(self, matrixType):
        matrixType = matrixType.lower()
        if matrixType not in ['normal', 'optimized']:
            raise KeyError("Expected one of ['normal', 'optimized'], got {}".format(matrixType))
        else:
            self.matrixType = matrixType

    @pyqtSlot()
    def saveCameraMatrix(self):
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
    def setFrameType(self, currentText):
        currentText = currentText.lower()
        currentIndex = self.stream.currentFrameIdx
        if currentText == "source":
            imgs = self.sourceImgs
        elif currentText == "detected":
            imgs = self.detectedImgs
        elif currentText == "corrected":
            imgs = self.correctedImgs
        else:
            raise KeyError("Expected one of ['source', 'detected', 'corrected'], got {}".format(currentText))
        self.stream = ImageListVideoStream(imgs)
        self._updateImgProvider()
        self.stream.currentFrameIdx = self.validateFrameIdx(currentIndex -1) # reset to previous position
        self.getImg()
    
    def getImg(self):
        if self.stream.currentFrameIdx < self.nFrames and self.stream.currentFrameIdx >= -1:
            try:
                self.display.reload()
                self.display.setProperty('value', self.stream.currentFrameIdx)
            except EOFError:
                self.timer.stop()
        else:
            self.timer.stop()

class ImageListVideoStream(object):
    def __init__(self, imgsList):
        self.imgs = imgsList
        self.currentFrameIdx = 0

    def read(self):
        """
        Returns the next frame after updating the count
        
        :return: frame
        :rtype: video_frame.Frame
        
        :raises: EOFError when end of stream is reached
        """
        if self.currentFrameIdx > (len(self.imgs) - 2):
            raise EOFError("End of recording reached")
        img = self.imgs[self.currentFrameIdx]
        frame = Frame(img)
        self.currentFrameIdx += 1
        return frame

class TrackerIface(QObject):
    def __init__(self, app, context, parent=None, main=None):
        QObject.__init__(self, parent)
        self.app = app # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context
        self.main = main
        
        self.positions = []
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.getImg)
        
        self.timerSpeed = 20
        
        self.roi = None

    @pyqtSlot(QVariant, result=QVariant)
    def getRow(self, idx):
        idx = int(idx)
        if 0 <= idx < len(self.positions):
            result = [str(idx)]
            result += [str(var) for var in self.positions[idx]]
            result += [str(var) for var in self.distancesFromArena[idx]]
            return  result
        else:
            return -1

    @pyqtSlot()
    def load(self):
        self.tracker = GuiTracker(self.main.srcPath, destFilePath=None,
                                nBackgroundFrames=1, plot=True,
                                fast=False, callback=None)
        self.tracker.roi = None
                
        self.nFrames = self.tracker._stream.nFrames - 1
        self.currentFrameIdx = self.tracker._stream.currentFrameIdx
        
        if self.main.endFrameIdx == -1:
            self.main.endFrameIdx = self.nFrames
        
        self.display = self.win.findChild(QObject, "trackerDisplay")
        self.display.setProperty('maximumValue', self.nFrames)

        engine = self.ctx.engine()
        self.imageProvider = CvImageProvider(requestedImType='pixmap', stream=self)
        engine.addImageProvider("trackerprovider", self.imageProvider)
        
        self.analysisImageProvider = PyplotImageProvider(fig=None)
        engine.addImageProvider("analysisprovider", self.analysisImageProvider)
        self.analysisImageProvider2 = PyplotImageProvider(fig=None)
        engine.addImageProvider("analysisprovider2", self.analysisImageProvider2)

    @pyqtSlot()
    def start(self):
        self.positions = [] # reset between runs
        self.distancesFromArena = []
        
        self.tracker._stream.bgStartFrame = self.main.bgFrameIdx
        nBackgroundFrames = self.main.nBgFrames
        self.tracker._stream.bgEndFrame = self.main.bgFrameIdx + nBackgroundFrames - 1
        self.tracker.trackFrom = self.main.startFrameIdx
        self.tracker.trackTo = self.main.endFrameIdx if (self.main.endFrameIdx > 0) else None
        
        self.tracker.threshold = self.main.detectionThreshold
        self.tracker.minArea = self.main.objectsMinArea
        self.tracker.maxArea = self.main.objectsMaxArea
        self.tracker.teleportationThreshold = self.main.teleportationThreshold
        
        self.tracker.nSds = self.main.nSds
        self.tracker.clearBorders = self.main.clearBorders
        self.tracker.normalise = self.main.normalise
        self.tracker.extractArena = self.main.extractArena
        
        if self.roi is not None:
            self.tracker.setRoi(self.roi)
            
        self.timer.start(self.timerSpeed)

    @pyqtSlot()
    def stop(self):
        self.timer.stop()
        self.tracker._stream.stopRecording('Recording stopped manually')
        
    @pyqtSlot()
    def save(self):
        diag = QFileDialog()
        destPath = diag.getSaveFileName(parent=diag,
                                    caption='Save file',
                                    directory=os.getenv('HOME'), 
                                    filter="Text (*.txt *.dat *.csv)")
        destPath = destPath[0]
        if destPath:
            self.write(destPath)

    @pyqtSlot(QVariant)
    def setFrameType(self, outputType):
        self.outputType = outputType.lower()

    @pyqtSlot()
    def analyseAngles(self):
        fig, ax = plt.subplots()
        angles = video_analysis.getAngles(self.positions)
        video_analysis.plotAngles(angles, self.getSamplingFreq())
        self.analysisImageProvider._fig = fig

    @pyqtSlot()
    def saveAnglesFig(self):
        diag = QFileDialog()
        destPath = diag.getSaveFileName(parent=diag,
                                    caption='Save file',
                                    directory=os.getenv('HOME'), 
                                    filter="Image (*.png *.jpg)")
        destPath = destPath[0]
        if destPath:
            imsave(destPath, self.analysisImageProvider.getArray())

    @pyqtSlot()
    def analyseDistances(self):
        fig, ax = plt.subplots()
        distances = video_analysis.posToDistances(self.positions)
        video_analysis.plotDistances(distances, self.getSamplingFreq())
        self.analysisImageProvider2._fig = fig
        
    def getSamplingFreq(self):
        return self.tracker._stream.fps

    def write(self, dest):
        with open(dest, 'w') as outFile:
            writer = csv.writer(outFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for fid, row in enumerate(self.positions):
                writer.writerow([fid]+list(row))

    @pyqtSlot(result=QVariant)
    def getFrameIdx(self):
        return str(self.tracker._stream.currentFrameIdx)
        
    @pyqtSlot(QVariant, QVariant, QVariant, QVariant, QVariant)
    def setRoi(self, width, height, x, y, diameter):        
        streamWidth, streamHeight = self.tracker._stream.size # flipped for openCV
        horizontalScalingFactor = streamWidth / width
        verticalScalingFactor = streamHeight / height
        
        radius = diameter / 2.0
        scaledX = (x + radius) * horizontalScalingFactor
        scaledY = (y + radius) * verticalScalingFactor
        scaledRadius = radius * horizontalScalingFactor
        
        self.roi = Circle((scaledX, scaledY), scaledRadius)

    def read(self):
        try:
            self.currentFrameIdx = self.tracker._stream.currentFrameIdx + 1
            result = self.tracker.trackFrame(requestedOutput=self.outputType)
        except cv2.error:
            self.timer.stop()
            self.tracker._stream.stopRecording('Detection issue, check your parameters')
            return None
        if result is not None:
            img, position, distances = result
            self.positions.append(position)
            self.distancesFromArena.append(distances)
            return img
        else:
            self.positions.append((-1, -1))
            self.distancesFromArena.append((-1, -1))

    def getImg(self):
        if self.tracker._stream.currentFrameIdx < self.nFrames:
            self.display.reload()
            self.display.setProperty('value', self.tracker._stream.currentFrameIdx)
        else:
            self.timer.stop()
            self.tracker._stream.stopRecording('End of recording reached')

class RecorderIface(TrackerIface):
    def __init__(self, app, context, parent=None, main=None):
        TrackerIface.__init__(self, app, context, parent, main)
        
    @pyqtSlot()
    def load(self):
        pass
        
    @pyqtSlot()
    def start(self):
        self.positions = [] # reset between runs
        self.distancesFromArena = []
        
        bgStart = self.main.bgFrameIdx
        nBackgroundFrames = self.main.nBgFrames
        trackFrom = self.main.startFrameIdx
        trackTo = self.main.endFrameIdx if (self.main.endFrameIdx > 0) else None
        
        threshold = self.main.detectionThreshold
        minArea = self.main.objectsMinArea
        maxArea = self.main.objectsMaxArea
        teleportationThreshold = self.main.teleportationThreshold
        
        nSds = self.main.nSds
        clearBorders = self.main.clearBorders
        normalise = self.main.normalise
        extractArena = self.main.extractArena
        
        self.tracker = GuiTracker(srcFilePath=None, destFilePath=self.main.destPath,
                                threshold=threshold, minArea=minArea, maxArea=maxArea,
                                teleportationThreshold=teleportationThreshold,
                                bgStart=bgStart, trackFrom=trackFrom, trackTo=trackTo,
                                nBackgroundFrames=nBackgroundFrames, nSds=nSds,
                                clearBorders=clearBorders, normalise=normalise,
                                plot=True, fast=False, extractArena=extractArena,
                                callback=None)

        self.display = self.win.findChild(QObject, "recording")

        self.imageProvider = CvImageProvider(requestedImType='pixmap', stream=self)
        engine = self.ctx.engine()
        engine.addImageProvider("recorderprovider", self.imageProvider)
        
        if self.roi is not None:
            self.tracker.setRoi(self.roi)
        else:
            self.tracker.roi = None
        
        self.timer.start(self.timerSpeed)
        
    def getSamplingFreq(self):
        return 1.0 / (self.timerSpeed / 1000.0) # timer speed in ms
        
    @pyqtSlot(result=QVariant)
    def camDetected(self):
        cap = cv2.VideoCapture(0)
        detected = False
        if cap.isOpened():
            detected = True
        cap.release()
        return detected

    def getImg(self):
        self.display.reload()
        
    def read(self):
        try:
            self.currentFrameIdx = self.tracker._stream.currentFrameIdx + 1
            result = self.tracker.trackFrame(record=True, requestedOutput=self.outputType)
        except cv2.error as e:
            self.timer.stop()
            self._stream.stopRecording('Error {} stopped recording'.format(e))
            print('Detection issue, check your parameters')
            return None
        if result is not None:
            img, position, distances = result
            self.positions.append(position)
            self.distancesFromArena.append(distances)
            return img
        else:
            self.positions.append((-1, -1))
            self.distancesFromArena.append((-1, -1))

class CvImageProvider(QQuickImageProvider):
    
    def __init__(self, requestedImType='img', stream=None):
        if requestedImType == 'img':
            imType = QQuickImageProvider.Image
        elif requestedImType == 'pixmap':
            imType = QQuickImageProvider.Pixmap
        else:
            raise NotImplementedError('Unknown type: {}'.format(requestedImType))
        QQuickImageProvider.__init__(self, imType)
        self._stream = stream

    def requestPixmap(self, id, qSize):
        """
        Called if imType == Pixmap
        """
        qimg, qSize = self.requestImage(id, qSize)
        img = QPixmap.fromImage(qimg)
        return img, qSize
        
    def requestImage(self, id, qSize):
        """
        Called if imType == Image
        """
        size = self.getSize(qSize)
        qimg = self.getBaseImg(size)
        return qimg, QSize(*size)
        
    def getSize(self, qSize):
        if qSize.isValid():
            size = (qSize.width(), qSize.height())
        else:
            size = (512, 512)
        return size
        
    def getRndmImg(self, size):
        img = np.random.random(size)
        img *= 125
        img = img.astype(np.uint8)
        img = np.dstack([img]*3)
        return img
        
    def _writeErrorMsg(self, img, imgSize):
        text = "No contour found at frame: {}".format(self._stream.currentFrameIdx)
        text2 = "Please check your parameters"
        text3 = "And ensure specimen is there"
        x = 10
        y = imgSize[0]/2
        ySpacing = 40
        yellow = (255, 255, 0)
        fontSize = 75/100.0
        cv2.putText(img, text, (x, y), 2, fontSize, yellow)
        y += ySpacing
        cv2.putText(img, text2, (x, y), 2, fontSize, yellow)
        y += ySpacing
        cv2.putText(img, text3, (x, y), 2, fontSize, yellow)

    def getBaseImg(self, size):
        if self._stream is not None:
            img = self._stream.read()
            if img is not None:
                img = img.color().copy()
                size = img.shape[:2]
            else:                
                img = self.getRndmImg(size)
                self._writeErrorMsg(img, size)
        else:
            img = self.getRndmImg(size)
        img = (img[:, :, :3]).copy() # For images with transparency channel, take only first 3 channels
        w, h = size
        qimg = QImage(img, h, w, QImage.Format_RGB888)
        return qimg

class PyplotImageProvider(QQuickImageProvider):
    
    def __init__(self, fig=None):
        QQuickImageProvider.__init__(self, QQuickImageProvider.Pixmap)
        self._fig = fig

    def requestPixmap(self, id, qSize):
        """
        Called if imType == Pixmap
        """
        qimg, qSize = self.requestImage(id, qSize)
        img = QPixmap.fromImage(qimg)
        return img, qSize
        
    def requestImage(self, id, qSize):
        """
        Called if imType == Image
        """
        size = self.getSize(qSize)
        qimg = self.getBaseImg(size)
        return qimg, QSize(*size)
        
    def getSize(self, qSize):
        return (qSize.width(), qSize.height()) if qSize.isValid() else (512, 512)
        
    def getRndmImg(self, size):
        img = np.random.random(size)
        img *= 125
        img = img.astype(np.uint8)
        img = np.dstack([img]*3)
        return img
        
    def getArray(self):
        self._fig.canvas.draw()
        width, height = self._fig.canvas.get_width_height()
        img = self._fig.canvas.tostring_rgb()
        img = np.fromstring(img, dtype=np.uint8).reshape(height, width, 3)
        return img

    def getBaseImg(self, size):
        if self._fig is not None:
            img = self.getArray()
            size = img.shape[:2]
        else:
            img = self.getRndmImg(size)
        w, h = size
        qimg = QImage(img, h, w, QImage.Format_RGB888)
        return qimg

def main():
    app = QApplication(sys.argv)
    
    appEngine = QQmlApplicationEngine()
    
    context = appEngine.rootContext()
    appEngine.addImageProvider('viewerprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('trackerprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('recorderprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('calibrationprovider', CvImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('analysisprovider', PyplotImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.addImageProvider('analysisprovider2', PyplotImageProvider()) # Hack to make qml believe provider is valid before its creation
    appEngine.load(QUrl('./qml/MouseTracker.qml'))
    
    win = appEngine.rootObjects()[0]
    
    # REGISTER PYTHON CLASSES WITH QML
    iface = MainIface(app, context, win)
    viewer = Viewer(app, context, win, iface)
    tracker = TrackerIface(app, context, win, iface)
    recorder = RecorderIface(app, context, win, iface)
    calibrater = CalibrationIface(app, context, win, iface)
    
    context.setContextProperty('py_iface', iface)
    context.setContextProperty('py_viewer', viewer)
    context.setContextProperty('py_tracker', tracker)
    context.setContextProperty('py_recorder', recorder)
    context.setContextProperty('py_calibration', calibrater)
    
    win.show()
    try:
        apcode = app.exec_()
    except:
        print('there was an issue')
    finally:
        sys.exit(apcode)

if __name__ == '__main__':
    main()
