import os
import platform

import numpy as np
from scipy import misc
import cv2

isPi = (platform.machine()).startswith('arm')
"""
Inspired from:
http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
"""

class CameraCalibration(object):
    """
    A class to be used to compensate for optical distortion in images.
    It can compute the distortion parameters (camera matrix) from a set of images containing 
    a chessboard pattern acquired with the aforementioned camera (see link above for more details).
    
    Once the distortion parameters are known, it can be used to undistort images 
    supplied to the remap() and inPlaceRemap() methods. These images must be once more acquired
    with the same parameters as the calibration images.
    
    The remap method is optimised differently for the raspberry pi
    """
    
    VALID_IMAGE_TYPES = ('.png', '.jpg', '.jpeg', '.ppm', '.tiff', '.tif', '.bmp')
    INTERP_METHOD = cv2.INTER_NEAREST if isPi else cv2.INTER_LINEAR
    
    def __init__(self, chessWidth, chessHeight):
        """
        :param int chessWidth: The number of rows of corners to be detected in the pattern
        :param int chessHeight: The number of columns of corners to be detected in the pattern
        """
        self.chessWidth = chessWidth
        self.chessHeight = chessHeight
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001) # termination criteria

    def _getExt(self, path):
        """
        Returns the extension form the supplied path
        
        :param string path: The path to process
        """
        return (os.path.splitext(path))[1]

    def getImages(self, srcFolder):
        """
        Load the images from the given folder. This function will load all images that are of
        VALID_IMAGE_TYPES in the the folder.
        
        :param string srcFolder: The source folder where the images are stored
        """
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
        """
        Compute the camera matrix, optimised camera matrix and distortion coefficients
        """
        
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
        """        
        :param img: The source image to take as reference
        """
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
        self.optimiseMatrix(refFrame)
        mapX, mapY = self.getMap(refFrame)
        self.mapX = mapX
        self.mapY = mapY
        
        self.srcImgs = srcImgs
        self.detectedImgs = detectedImgs
        self.correctedImgs = self.correctImgs(srcImgs)

    def getMap(self, refFrame):
        """
        Returns the x and y maps used to remap the pixels in the remap function.
        
        :param refFrame: An image with the same property as the calibration and target frames.
        """
        h, w = refFrame.shape[:2]
        mapX, mapY = cv2.initUndistortRectifyMap(self.cameraMatrix, self.distortionCoeffs, None,
                                                self.optimalCameraMatrix, (w, h), 5)
        mapX2, mapY2 = cv2.convertMaps(mapX, mapY, cv2.CV_16SC2)
        return (mapX2, mapY2)

    def remap(self, frame):
        """
        Corrects the distortion in 'frame' using the x and y maps computed by getMap()
        
        :param frame: The frame to undistort        
        :returns: The undistorted image
        """
        return cv2.remap(frame.copy(), self.mapX, self.mapY, CameraCalibration.INTERP_METHOD)
        
    def inPlaceRemap(self, frame):
        """
        Corrects the distortion in 'frame' using the x and y maps computed by getMap()
        Contrary to remap() the correction is done in place on 'frame' and the method
        returns None
        
        :param frame: The frame to undistort
        """
        cv2.remap(frame, self.mapX, self.mapY, CameraCalibration.INTERP_METHOD)

    def correctImgs(self, imgsList):
        """
        Corrects distortion on a complete list of images
        
        :param imgsList: The list of images to undistort
        """
        return [self.remap(img) for img in imgsList]
    
class CameraCalibrationException(Exception):
    """
    A Camera calibration specific exception meant to be raised
    if some type problem occurs during calibration
    """
    pass
