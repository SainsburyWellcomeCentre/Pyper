# -*- coding: utf-8 -*-
"""
**************
The roi module
**************

This module is used to check the position of the tracked specimen relative to a region of interest (ROI)

:author: crousse
"""
import math
import os
import shutil
import tarfile
import tempfile

import numpy as np
from math import radians, cos, sin, sqrt
import cv2
from cv2 import norm

from pyper.contours.object_contour import ObjectContour

try:
    from cv2 import cv
    FILLED = cv.CV_FILLED
except ImportError:  # removes dependency to cv2.cv outside of video_writer
    FILLED = -1


class RoiCollection(object):
    def __init__(self, rois_list=None):
        self.rois = [] if rois_list is None else rois_list

    def __len__(self):
        return len(self)

    def __iter__(self):
        for roi in self.rois:
            yield roi

    def __getitem__(self, item):  # TODO: implement dict version too with uuid as key
        return self.rois[item]

    def append(self, item):
        self.rois.append(item)

    def fmt_is_available(self, fmt):
        fmts = (fmt for fmt, _ in shutil.get_archive_formats())
        return fmt in fmts

    def compress(self, dest_file_path):
        dest_file_path_no_ext, ext = os.path.splitext(dest_file_path)
        tmp_dir = tempfile.mkdtemp()
        for i, roi in enumerate(self.rois):
            roi.save(os.path.join(tmp_dir, "roi_{}.roi".format(i)))

        for _fmt in ('bztar', 'gztar', 'zip', 'tar'):
            if self.fmt_is_available(_fmt):
                fmt = _fmt
                break
        old_dir = os.curdir
        os.chdir(tmp_dir)  # To prevent having subdirectories
        shutil.make_archive(dest_file_path_no_ext, fmt)
        os.chdir(old_dir)
        if os.path.exists(dest_file_path):
            shutil.rmtree(tmp_dir)

    def decompress(self, archive_file_path):
        tmp_dir = tempfile.mkdtemp()
        archive_name = os.path.split(archive_file_path)[1]
        tmp_archive_file_path = os.path.join(tmp_dir, archive_name)
        shutil.copy(archive_file_path, tmp_archive_file_path)
        with tarfile.open(tmp_archive_file_path) as tar:
            tar.extractall(path=tmp_dir)
        archive_dir = os.path.join(tmp_dir, '.')
        for file_name in os.listdir(archive_dir):
            if file_name.endswith('.roi'):
                file_path = os.path.join(archive_dir, file_name)
                self.append(Roi.from_data(Roi.load(file_path)))
        shutil.rmtree(tmp_dir)


class Roi(object):
    """
    A generic ROI object meant to be sub-classed by specific ROI shapes.
    It is used to obtain information about points relative to itself.
    """
    def __init__(self):
        self.points = None
        self.centre = None
        self.width = None
        self.height = None
        self.contour = None
    
    def contains_point(self, point):
        """
        Returns True if the point is in the ROI
        
        :param tuple point: the (x, y) point to check
        """
        return cv2.pointPolygonTest(self.points, point, False) > 0

    def contains_contour(self, contour):
        for p in contour:
            if not self.contains_point(tuple(p[0])):  # at least one point outside self
                return False
        return True
        
    def dist_from_border(self, point):
        """
        Returns the distance from the point to the border of the ROI
        
        :param tuple point: the (x, y) point to check
        """
        return cv2.pointPolygonTest(self.points, point, True)
        
    def dist_from_centre(self, point):
        """
        Returns the distance from the point to the centre of mass of the ROI
        
        :param tuple point: the (x, y) point to check
        """
        return norm(self.centre, point)

    def to_mask(self, frame):
        mask = frame.copy()  # TODO: extract to roi.to_mask
        mask.fill(0)
        cv2.drawContours(mask, [self.points], 0, 255, FILLED)
        return mask

    def save(self, dest):  # FIXME: should be class specific
        t = str(type(self)).strip("'<>").split('.')[-1].lower()
        with open(dest, 'w') as out_file:
            out_file.write("{}\n".format(t))
            out_file.write("{}\n".format(self.centre[0]))
            out_file.write("{}\n".format(self.centre[1]))
            out_file.write("{}\n".format(self.width))
            out_file.write("{}\n".format(self.height))
            for pnt in self.points.squeeze():
                out_file.write("{}, {}\n".format(*pnt))  # TODO: format

    def get_data(self):  # default method to be overwritten
        t = str(type(self)).strip("'<>").split('.')[-1].lower()
        # Uses string to have same interface as save
        roi_data = [t, str(self.centre[0]), str(self.centre[1]), str(self.width), str(self.height)]
        for pnt in self.points.squeeze():
            roi_data.append('{}, {}'.format(*pnt))
        return roi_data

    @staticmethod
    def load(src_path):
        with open(src_path, 'r') as in_file:
            lines = in_file.readlines()
        return lines

    @staticmethod
    def from_data(data):
        roi_class = data[0].strip()
        centre_x, centre_y, width, height = [float(ln.strip()) for ln in data[1:5]]
        points = [[(float(p.strip())) for p in ln.split(',')] for ln in data[5:]]
        if roi_class == 'ellipse':
            return Ellipse(centre_x, centre_y, width, height)
        elif roi_class == 'rectangle':
            top_left_x = centre_x - width / 2.
            top_left_y = centre_y - height / 2.
            return Rectangle(top_left_x, top_left_y, width, height)
        elif roi_class == 'freehand':
            return FreehandRoi(points)
        else:
            raise ValueError('Expected one of ("ellipse", "rectangle", "freehand"), got "{}"'.format(roi_class))


class Circle(Roi):
    """
    A circle Object that contains an array of points distributed on its perimeter
    
    Use as follows:
    
    >>> roi = Circle((256, 256), 30) # creates a circle of radius 30 at centre 256, 256
    >>> specimen_position = (250, 242)
    >>> if roi.contains_point(specimen_position):
    >>>     print('The specimen entered the ROI')
    """

    def __init__(self, centre, radius):
        """
        Initialises a circle
        
        :param tuple centre: the centre of the circle
        :param int radius: the radius in pixels
        """
        Roi.__init__(self)
        self.centre = centre
        self.radius = radius
        points = self.get_points().astype(np.int32)
        self.points = np.expand_dims(points, axis=1)
        self.contour = ObjectContour(self.points, contour_type='circle')
        
    def circle_point(self, angle):
        """
        Gets a point on the circle at the given angle
        
        :param angle: the angle in radians
        """
        centre = self.centre
        radius = self.radius
        x = centre[0] + radius * cos(angle)
        y = centre[1] + radius * sin(angle)
        return x, y

    def get_points(self):
        """
        Get 360 points evenly spaced around the circle perimeter
        
        :return np.array points: the list of points.
        """
        n_points = 360
        points = np.empty((n_points, 2), dtype=np.float32)
        for i in range(n_points):
            points[i] = self.circle_point(radians(i))
        return points


class Rectangle(Roi):

    def __init__(self, top_left_x, top_left_y, width, height):
        Roi.__init__(self)
        self.top_left_point = (top_left_x, top_left_y)
        self.width = width
        self.height = height
        self.centre = (int(top_left_x + (width / 2)), int(top_left_y + (height / 2)))
        points = self.get_points().astype(np.int32)
        self.points = np.expand_dims(points, axis=1)
        self.contour = ObjectContour(self.points, contour_type='rectangle')

    def get_points(self):
        n_points = 4  # the 4 corners
        points = np.empty((n_points, 2), dtype=np.float32)
        top_x, top_y = self.top_left_point
        points[0] = self.top_left_point
        points[1] = (top_x + self.width, top_y)  # FIXME: use point type instead
        points[2] = (top_x + self.width, top_y + self.height)
        points[3] = (top_x, top_y + self.height)
        return points

    def get_data(self):
        t = 'rectangle'
        # Uses string to have same interface as save
        roi_data = [t, str(self.top_left_point[0]), str(self.top_left_point[1]), str(self.width), str(self.height)]
        for pnt in self.points.squeeze():
            roi_data.append('{}, {}'.format(*pnt))
        return roi_data


class Ellipse(Roi):
    def __init__(self, centre_x, centre_y, width, height):
        Roi.__init__(self)
        self.centre = (centre_x, centre_y)
        self.top_left_point = (centre_x - width / 2., centre_y - height / 2.)
        self.width = width
        self.height = height
        points = self.get_points().astype(np.int32)
        self.points = np.expand_dims(points, axis=1)
        self.contour = ObjectContour(self.points, contour_type='ellipse')

    def __compute_ellipse(self, semi_major, semi_minor, xs):
        return np.array([(semi_major / semi_minor) * sqrt(semi_minor**2 - x**2) for x in xs])

    def get_points(self):
        n_points = 200
        semi_minor = self.height / 2.
        semi_major = self.width / 2.
        xs = np.linspace(-semi_major, semi_major, math.ceil(n_points/2.))  # FIXME: inverted ?
        ys = self.__compute_ellipse(semi_minor, semi_major, xs)  # FIXME: inverted ?
        ys = np.hstack((ys, -ys[::-1])) + self.centre[1]
        xs = np.hstack((xs, xs[::-1])) + self.centre[0]
        points = np.column_stack((xs, ys)).astype(np.float32)
        return points

    def get_data(self):
        t = 'ellipse'
        # Uses string to have same interface as save
        roi_data = [t, str(self.top_left_point[0]), str(self.top_left_point[1]), str(self.width), str(self.height)]
        for pnt in self.points.squeeze():
            roi_data.append('{}, {}'.format(*pnt))
        return roi_data


class FreehandRoi(Roi):
    def __init__(self, points):
        Roi.__init__(self)
        points = np.array(points, dtype=np.int32)
        self.points = np.expand_dims(points, axis=1)
        self.__bounding_rect = cv2.boundingRect(self.points)
        self.width, self.height = self.get_width_height()
        self.centre = self.get_centre()
        self.contour = ObjectContour(self.points, contour_type='raw')

    def get_width_height(self):
        return self.__bounding_rect[2], self.__bounding_rect[3]

    def get_centre(self):
        return self.__bounding_rect[:2]


roi_classes = {
    'circle': Circle,
    'ellipse': Ellipse,
    'rectangle': Rectangle,
    'freehand': FreehandRoi
}
