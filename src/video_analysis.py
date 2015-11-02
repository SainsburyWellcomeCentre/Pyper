"""
*************************
The video_analysis module
*************************

This module is supplied for basic analysis of the position data. It should be used to give you a quick overview of the trajectory behaviour.
However, please note that analysis is not the main goal of this software package so functionalities are limited in this module.

:author: crousse
"""

from __future__ import division

import math

from scipy.integrate import cumtrapz
import numpy as np
import numpy.linalg as la
from scipy.ndimage.filters import gaussian_filter as gauFit
from matplotlib import pyplot as plt
import matplotlib.cm as cm
    
def vectorsToAngle(v1, v2):
    """
    Returns the angle in radians between vectors 'v1' and 'v2'
    """
    cosang = np.dot(v1, v2)
    sinang = la.norm(np.cross(v1, v2))
    angle = np.arctan2(sinang, cosang)
    angle = np.pi - angle
    return angle

def pointsToAngle(a, b, c):
    """
    Converts points A, B, C (np.array)
    to angle in degrees with sign
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    angle = vectorsToAngle(ba, bc)
    if ((b[0] - a[0])*(c[1] - a[1]) - (b[1] - a[1])*(c[0] - a[0])) > 0:
        angle *= -1
    return np.degrees(angle)
    
def testPointsToAngle():
    assert pointsToAngle(np.array([-1, -1]), np.array([0, 0]), np.array([1, 1])) == 0, "Line vector didn't return 0"
    assert pointsToAngle(np.array([-1, -1]), np.array([0, 0]), np.array([0, 1])) == -45
    assert pointsToAngle(np.array([-1, -1]), np.array([0, 0]), np.array([1, 0])) == 45
    assert pointsToAngle(np.array([0, 1]), np.array([0, 0]), np.array([1, -1])) == -45
    assert pointsToAngle(np.array([0, 1]), np.array([0, 0]), np.array([-1, -1])) == 45
    
def plotTrack(positions, backGroundImg):
    """
    Plots the trajectory of the mouse from positions onto backGroundImg
    Positions is a list of (x,y) coordinates pairs
    """
    plt.imshow(backGroundImg, cmap = cm.Greys_r);
    
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    plt.plot(xs, ys);

def posToDistances(positions):
    """
    Extracts distances form the positions list
    """
    distances=[]
    for i in range(1, len(positions)):
        p1 = positions[i-1]
        p2 = positions[i]
        for v in p1+p2:
            if (v != -1) and (type(v) not in [float, np.float64, np.float32]):
                raise TypeError("Index {}, expected type float, got {}".format(i, type(v)))
        distance = math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)
        distances.append(distance)
    return distances

def readPositions(srcFilePath):
    """
    Reads a positions dat file into a list of positions
    
    .. warning:
        It assumes positions are 2nd and 3rd columns of the file
        and the file is tab separated
    """
    with open(srcFilePath, 'r') as inFile:
        positions = inFile.readlines()[1:] # skip header
    positions = [p.split('\t')[1:3] for p in positions]
    positions = [np.array([float(p[0]), float(p[1])]) for p in positions]
    return positions
    
def filterPositions(positions, kernel):
    """
    Gaussian smoothes the positions using the supplied kernel
    """
    xs = gauFit([p[0] for p in positions], kernel)
    ys = gauFit([p[1] for p in positions], kernel)
    positions = np.array(zip(xs, ys))
    return positions

def getPos(nb):
    """ Converts negative numbers to 0"""
    return nb if nb > 0 else 0
        
def getNeg(nb):
    """ Converts positive numbers to 0"""
    return nb if nb < 0 else 0

def getAngles(positions):
    """
    Computes the angles between 2 successive points
    from the positions list
    """
    angles = []
    for i in range(2, len(positions)):
        a = positions[i-2]
        b = positions[i-1]
        c = positions[i]
        if a == b == c:
           angles.append(0)
        else:
            angles.append(pointsToAngle(a, b, c))
    return angles
        
def plotAngles(angles, samplingFreq):
    xVect = np.array(range(len(angles))) / samplingFreq
    zeroLine = np.zeros(len(angles))
    plt.plot(xVect, angles, linewidth=0.1)
    plt.plot(xVect, zeroLine, color='g', linewidth=3, linestyle='--')
    plt.ylim([-180, 180])
    plt.ylabel('angle (degrees)')
    plt.xlabel('time (s)')
    plt.fill_between(xVect, angles, zeroLine, where=angles>zeroLine, color='b', label='Left turns')
    plt.fill_between(xVect, angles, zeroLine, where=angles<zeroLine, color='r', label='Right turns')
    
def plotDistances(distances, samplingFreq):
    xVect = np.array(range(len(distances))) / samplingFreq
    plt.ylim([0, 100])
    plt.ylabel('distance (pixels)')
    plt.xlabel('time (s)')
    plt.plot(xVect, distances, label='Distance (AU)')

def writeDataList(data, outPath):
    data = [str(d)+'\n' for d in data] + ['\n']
    with open(outPath, 'w') as outFile:
        outFile.writelines(data)

def plotIntegrals(angles, samplingFreq):
    anglesLeft = [getPos(a) for a in angles]
    anglesRight = [getNeg(a) for a in angles]
    leftTurnIntegral = cumtrapz(anglesLeft, dx=(1/samplingFreq), axis=0)
    rightTurnIntegral = cumtrapz(anglesRight, dx=(1/samplingFreq), axis=0)
    totalIntegral = cumtrapz(angles, dx=(1/samplingFreq), axis=0)
    xVect = np.array(range(len(leftTurnIntegral))) / samplingFreq

    plt.ylim([-180, 180])
    plt.plot(xVect, leftTurnIntegral, color='b', label='Left turns')
    plt.plot(xVect, rightTurnIntegral, color='r', label='Right turns')
    plt.plot(xVect, totalIntegral, color='g', label='Both turns')
    plt.legend(loc='best')
