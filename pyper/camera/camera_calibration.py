import numpy as np
import os
import platform
from scipy import misc

import cv2

from pyper.exceptions.exceptions import CameraCalibrationException

is_pi = (platform.machine()).startswith('arm')
"""
Inspired by:
http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
"""


class CameraCalibration(object):
    """
    A class to be used to compensate for optical distortion in images.
    It can compute the distortion parameters (camera matrix) from a set of images containing 
    a chessboard pattern acquired with the aforementioned camera (see link above for more details).
    
    Once the distortion parameters are known, it can be used to correct distortion in images
    using the remap() and inPlaceRemap() methods. These images must be once more acquired
    with the same parameters as the calibration images.
    
    The remap method is optimised differently for the raspberry pi
    """
    
    VALID_IMAGE_TYPES = ('.png', '.jpg', '.jpeg', '.ppm', '.tiff', '.tif', '.bmp')
    INTERP_METHOD = cv2.INTER_NEAREST if is_pi else cv2.INTER_LINEAR
    
    def __init__(self, chess_width, chess_height):
        """
        :param int chess_width: The number of rows of corners to be detected in the pattern
        :param int chess_height: The number of columns of corners to be detected in the pattern
        """
        self.chess_width = chess_width
        self.chess_height = chess_height
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)  # termination criteria

    @staticmethod
    def _get_ext(path):
        """
        Returns the extension form the supplied path
        
        :param string path: The path to process
        """
        return (os.path.splitext(path))[1]

    def get_images(self, src_folder):
        """
        Load the images from the given folder. This function will load all images that are of
        VALID_IMAGE_TYPES in the the folder.
        
        :param string src_folder: The source folder where the images are stored
        """
        files = os.listdir(src_folder)
        images_names = sorted([f for f in files if self._get_ext(f) in CameraCalibration.VALID_IMAGE_TYPES])
        imgs = []
        img_paths = []
        for fname in images_names:
            img_path = os.path.join(src_folder, fname)
            imgs.append(misc.imread(img_path))
            img_paths.append(img_path)
        if len(imgs) == 0:
            raise IOError("No images found in folder {}. Please check you path".format(src_folder))
        self.img_paths = img_paths
        self.imgs = imgs

    def get_calibration_params(self, src_folder, return_imgs=False, sub_pixel=False):
        """Compute the camera matrix, optimised camera matrix and distortion coefficients"""
        
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        n_corners = self.chess_width * self.chess_height
        objp = np.zeros((n_corners, 3), np.float32)
        objp[:, :2] = np.mgrid[:self.chess_width, :self.chess_height].T.reshape(-1, 2)
        
        # Arrays to store object points and image points from all the images.
        obj_points = []  # 3d point in real world space
        img_points = []  # 2d points in image plane.

        src_imgs = []  # The list of images where corners were found
        detected_imgs = []  # The list of images with the corners drawn

        self.get_images(src_folder)
        original_images = [img.copy() for img in self.imgs]  # copy the list because openCV modifies in place
        for img, img_path in zip(original_images, self.img_paths):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(gray, (self.chess_width, self.chess_height))
            if found:
                print('Image {}, corners found'.format(img_path))
                obj_points.append(objp)
                if sub_pixel:
                    corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), self.criteria)
                img_points.append(corners)
                src_imgs.append(img.copy())
                cv2.drawChessboardCorners(img, (self.chess_width, self.chess_height), corners, found)
                detected_imgs.append(img)
            else:
                print('Image {}, no corners found'.format(img_path))
        calibration_results = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1])
        flag = calibration_results[0]
        if not flag:
            raise CameraCalibrationException("Calibration failed")
        return calibration_results, src_imgs, detected_imgs

    def optimise_matrix(self, img):
        """        
        :param img: The source image to take as reference
        """
        h, w = img.shape[:2]
        optimal_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.distortion_coeffs, (w, h), 1)
        self.optimal_camera_matrix = optimal_camera_matrix
        return optimal_camera_matrix
    
    def calibrate(self, src_folder, sub_pixel=False):
        """
        Computes the camera matrix from the images in the source folder supplied as argument
        The arrangement of the internal corners in the image are determined by chessWidth and chessHeight
        
        :param string src_folder: The Folder where the calibration images are stored
        :param int chess_width: The width of the internal chessboard pattern (minus the outer band)
        :param int chess_height: The height of the internal chessboard pattern (minus the outer band)
        :param bool sub_pixel: Use subpixel accuracy
        """

        calibration_results, src_imgs, detected_imgs = self.get_calibration_params(src_folder, return_imgs=True)
        flag, camera_matrix, distortion_coeffs, rvecs, tvecs = calibration_results
        self.camera_matrix = camera_matrix
        self.distortion_coeffs = distortion_coeffs

        refFrame = src_imgs[0]
        self.optimise_matrix(refFrame)
        map_x, map_y = self.get_map(refFrame)
        self.map_x = map_x
        self.map_y = map_y
        
        self.src_imgs = src_imgs
        self.detected_imgs = detected_imgs
        self.corrected_imgs = self.correct_imgs(src_imgs)

    def get_map(self, ref_frame):
        """
        Returns the x and y maps used to remap the pixels in the remap function.
        
        :param ref_frame: An image with the same property as the calibration and target frames.
        """
        h, w = ref_frame.shape[:2]
        map_x, map_y = cv2.initUndistortRectifyMap(self.camera_matrix, self.distortion_coeffs, None,
                                                 self.optimal_camera_matrix, (w, h), 5)
        map_x2, map_y2 = cv2.convertMaps(map_x, map_y, cv2.CV_16SC2)
        return map_x2, map_y2

    def correct_imgs(self, imgs_list):
        """
        Corrects distortion on a complete list of images
        
        :param imgs_list: The list of images to correct
        """
        return [self.remap(img) for img in imgs_list]

    def in_place_remap(self, frame):
        """
        Corrects the distortion in 'frame' using the x and y maps computed by getMap()
        Contrary to remap() the correction is done in place on 'frame' and the method
        returns None

        :param frame: The frame to correct
        """
        cv2.remap(frame, self.map_x, self.map_y, CameraCalibration.INTERP_METHOD)

    def remap(self, frame):
        """
        Corrects the distortion in 'frame' using the x and y maps computed by getMap()

        :param frame: The frame to correct
        :returns: The undistorted image
        """
        return cv2.remap(frame.copy(), self.map_x, self.map_y, CameraCalibration.INTERP_METHOD)
