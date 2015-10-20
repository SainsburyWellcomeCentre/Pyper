import os

import numpy as np
from scipy import misc
import cv2

"""
Inspired from:
http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
"""

class CameraCalibration(object):
    
    VALID_IMAGE_TYPES = ('.png', '.jpg', '.jpeg', '.ppm', '.tiff', '.tif', '.bmp')
    
    def __init__(self, chessWidth, chessHeight):
        self.chessWidth = chessWidth
        self.chessHeight = chessHeight
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001) # termination criteria

    def _getExt(self, path):
        return (os.path.splitext(path))[1]

    def getImages(self, srcFolder):
        files = os.listdir(srcFolder)
        imagesNames = sorted([f for f in files if self._getExt(f) in CameraCalibration.VALID_IMAGE_TYPES])
        imgs = []
        imgPaths = []
        for fname in imagesNames:
            imgPath = os.path.join(srcFolder, fname)
            imgs.append(misc.imread(imgPath))
            imgPaths.append(imgPath)
        if len(imgs) == 0:
            raise IOError("No images found in folder {}. Please check you path".format(srcFolder))
        self.imgPaths = imgPaths
        self.imgs = imgs

    def getCalibrationParams(self, srcFolder, returnImgs=False, subPixel=False):
        
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        nCorners = self.chessWidth*self.chessHeight
        objp = np.zeros((nCorners, 3), np.float32)
        objp[:,:2] = np.mgrid[:self.chessWidth, :self.chessHeight].T.reshape(-1, 2)
        
        # Arrays to store object points and image points from all the images.
        objPoints = [] # 3d point in real world space
        imgPoints = [] # 2d points in image plane.
        
        srcImgs = [] # The list of images where corners were found
        detectedImgs = [] # The list of images with the corners drawn

        self.getImages(srcFolder)
        originalImages = [img.copy() for img in self.imgs] # copy the list because openCV modifies in place
        for img, imgPath in zip(originalImages, self.imgPaths):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(gray, (self.chessWidth, self.chessHeight))
            if found:
                print('Image {}, corners found'.format(imgPath))
                objPoints.append(objp)
                if subPixel:
                    corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), self.criteria)
                imgPoints.append(corners)
                srcImgs.append(img.copy())
                cv2.drawChessboardCorners(img, (self.chessWidth, self.chessHeight), corners, found)
                detectedImgs.append(img)
            else:
                print('Image {}, no corners found'.format(imgPath))
        calibrationResults = cv2.calibrateCamera(objPoints, imgPoints, gray.shape[::-1])
        flag = calibrationResults[0]
        if not flag:
            raise CameraCalibrationException("Calibration falied")
        return calibrationResults, srcImgs, detectedImgs

    def optimiseMatrix(self, img):
        h, w = img.shape[:2]
        optimalCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distortionCoeffs, (w,h), 1)
        self.optimalCameraMatrix = optimalCameraMatrix
        return optimalCameraMatrix
    
    def calibrate(self, srcFolder, subPixel=False):
        """
        Computes the camera matrix from the images in the source folder supplied as argument
        The arrangement of the internal corners in the image are determined by chessWidth and chessHeight
        
        :param string srcFolder: The Folder where the calibration images are stored
        :param int chessWidth: The width of the internal chessboard pattern (minus the outer band)
        :param int chessHeight: The height of the internal chessboard pattern (minus the outer band)
        :param bool subPixel: Use subpixel accuracy
        """

        calibrationResults, srcImgs, detectedImgs = self.getCalibrationParams(srcFolder, returnImgs=True)
        flag, cameraMatrix, distortionCoeffs, rvecs, tvecs = calibrationResults
        self.cameraMatrix = cameraMatrix
        self.distortionCoeffs = distortionCoeffs

        refFrame = srcImgs[0]
        optimalCameraMatrix = self.optimiseMatrix(refFrame)
        mapX, mapY = self.getMap(refFrame)
        self.mapX = mapX
        self.mapY = mapY
        
        correctedImgs = self.correctImgs(srcImgs)
        
        return (cameraMatrix, optimalCameraMatrix, distortionCoeffs, srcImgs, detectedImgs, correctedImgs)

    def getMap(self, refFrame):
        h, w = refFrame.shape[:2]
        mapX, mapY = cv2.initUndistortRectifyMap(self.cameraMatrix, self.distortionCoeffs, None,
                                                self.optimalCameraMatrix, (w, h), 5)
        return (mapX, mapY)

    def remap(self, frame):
        return cv2.remap(frame.copy(), self.mapX, self.mapY, cv2.INTER_LINEAR)

    def correctImgs(self, imgsList):
        return [self.remap(img) for img in imgsList]
    
class CameraCalibrationException(Exception):
    """
    A Camera calibration specific exception meant to be raised
    if some type problem occurs during calibration
    """
    pass
