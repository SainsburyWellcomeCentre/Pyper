"""
*************************
The video_analysis module
*************************

This module is supplied for basic analysis of the position data. It should be used to give you a quick overview of the
trajectory behaviour. However, please note that analysis is not the main goal of this software package so functionality
is limited in this module.

:author: crousse
"""

from __future__ import division

import math
import matplotlib.cm as cm
import numpy as np
import numpy.linalg as la
from matplotlib import pyplot as plt
from scipy.integrate import cumtrapz
from scipy.ndimage.filters import gaussian_filter


def vectors_to_angle(v1, v2):
    """Returns the angle in radians between vectors 'v1' and 'v2'"""
    cos_ang = np.dot(v1, v2)
    sin_ang = la.norm(np.cross(v1, v2))
    angle = np.arctan2(sin_ang, cos_ang)
    angle = np.pi - angle
    return angle


def points_to_angle(a, b, c):
    """

    Converts points a, b, c (np.array) to angle in degrees with sign

    :param a:
    :param b:
    :param c:

    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    angle = vectors_to_angle(ba, bc)
    if ((b[0] - a[0])*(c[1] - a[1]) - (b[1] - a[1])*(c[0] - a[0])) > 0:
        angle *= -1
    return np.degrees(angle)


def plot_track(positions, background_img):
    """

    Plots the trajectory of the mouse from positions onto background_img
    Positions is a list of (x,y) coordinates pairs
    """
    plt.imshow(background_img, cmap=cm.Greys_r)
    
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    plt.plot(xs, ys)


def pos_to_distances(positions):
    """Extracts distances form the positions list"""
    distances = []
    for i in range(1, len(positions)):
        p1 = tuple(positions[i - 1])
        p2 = tuple(positions[i])
        for v in p1 + p2:
            if (v != -1) and (type(v) not in [float, np.float64, np.float32]):
                raise TypeError("Index {}, expected type float, got {}".format(i, type(v)))
        if p1 == (-1, -1) or p2 == (-1, -1):
            distance = 0
        else:
            distance = math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)
        distances.append(distance)
    return distances


def read_positions(src_file_path):
    """
    Reads a positions dat file into a list of positions
    
    .. warning:
        It assumes positions are 2nd and 3rd columns of the file
        and the file is tab separated

    :param str src_file_path:
    """
    with open(src_file_path, 'r') as in_file:
        positions = in_file.readlines()[1:]  # skip header
    positions = [p.split('\t')[1:3] for p in positions]
    positions = [np.array([float(p[0]), float(p[1])]) for p in positions]
    return positions


def filter_positions(positions, kernel):
    """Gaussian smoothes the positions using the supplied kernel"""
    xs = gaussian_filter([p[0] for p in positions], kernel)
    ys = gaussian_filter([p[1] for p in positions], kernel)
    positions = np.array(zip(xs, ys))
    return positions


def get_positive(nb):
    """Converts negative numbers to 0"""
    return nb if nb > 0 else 0


def get_negative(nb):
    """Converts positive numbers to 0"""
    return nb if nb < 0 else 0


def get_angles(positions):
    """
    Computes the angles between 2 successive points from the positions list
    :param positions:
    :return list angles:
    """
    angles = []
    for i in range(2, len(positions)):
        a = list(positions[i-2])
        b = list(positions[i-1])
        c = list(positions[i])
        if a == b == c:
            angles.append(0)
        else:
            angles.append(points_to_angle(a, b, c))
    return angles


def plot_angles(angles, sampling_freq):
    """

    :param angles:
    :param sampling_freq:
    """
    x_vect = np.array(range(len(angles))) / sampling_freq
    zero_line = np.zeros(len(angles))
    plt.plot(x_vect, angles, linewidth=0.1)
    plt.plot(x_vect, zero_line, color='g', linewidth=3, linestyle='--')
    plt.ylim([-180, 180])
    plt.ylabel('angle (degrees)')
    plt.xlabel('time (s)')
    plt.fill_between(x_vect, angles, zero_line, where=angles > zero_line, color='b', label='Left turns')
    plt.fill_between(x_vect, angles, zero_line, where=angles < zero_line, color='r', label='Right turns')


def plot_distances(distances, sampling_freq):
    """

    :param distances:
    :param sampling_freq:
    """
    x_vect = np.array(range(len(distances))) / sampling_freq
    plt.ylim([0, 10])
    plt.ylabel('distance (pixels)')
    plt.xlabel('time (s)')
    plt.plot(x_vect, distances, label='Distance (AU)')


def write_data_list(data, out_path):
    """

    :param data:
    :param out_path:
    """
    data = [str(d)+'\n' for d in data] + ['\n']
    with open(out_path, 'w') as outFile:
        outFile.writelines(data)


def plot_integrals(angles, sampling_freq):
    """

    :param angles:
    :param sampling_freq:
    """
    angles_left = [get_positive(a) for a in angles]
    angles_right = [get_negative(a) for a in angles]
    left_turn_integral = cumtrapz(angles_left, dx=(1 / sampling_freq), axis=0)
    right_turn_integral = cumtrapz(angles_right, dx=(1 / sampling_freq), axis=0)
    total_integral = cumtrapz(angles, dx=(1 / sampling_freq), axis=0)
    x_vect = np.array(range(len(left_turn_integral))) / sampling_freq

    plt.ylim([-180, 180])
    plt.plot(x_vect, left_turn_integral, color='b', label='Left turns')
    plt.plot(x_vect, right_turn_integral, color='r', label='Right turns')
    plt.plot(x_vect, total_integral, color='g', label='Both turns')
    plt.legend(loc='best')
