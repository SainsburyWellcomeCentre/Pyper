"""
Motion tracking, The command line interface

:author: crousse
"""

import os, sys, argparse, csv, shutil, tempfile

from configobj import ConfigObj

from tracking import Viewer, Tracker
from roi import Circle
from video_analysis import *

def coords(string):
    try:
        return int(string.strip())
    except:
        raise argparse.ArgumentError('Coordinates must be x, y. Got {}'.format(s))
############################## CLI #############################
configPath = os.path.expanduser(os.path.normcase('~/.motionTracking.conf'))
config = ConfigObj(configPath, encoding="UTF8", indent_type='    ', unrepr=True, create_empty=True, write_empty_values=True)
config.reload()

parser = argparse.ArgumentParser(prog=sys.argv[0])

parser.add_argument('videoFile', type=str, nargs='?', default='../resources/teleportingMouse.h264', help='Path (relative or absolute) of the video file to process.')
parser.add_argument('--threshold', type=int, default=config['tracker']['threshold'], help='The brightness level to threshold the image for feature detection. Default: %(default)s.')

parser.add_argument('-b', '--background-time', dest='bgTime', metavar='MM:SS', type=str, help='Time in mm:ss format for the background frame.')
parser.add_argument('-f', '--track-from', dest='trackFrom', metavar='MM:SS', type=str, help='Time in mm:ss format for the tracking start.')
parser.add_argument('-t', '--track-to', type=str, dest='trackTo', metavar='MM:SS', help='Time in mm:ss format for the tracking end.')
parser.add_argument('--n-background-frames', dest='nBackgroundFrames', type=int, default=config['tracker']['nBackgroundFrames'], help='The number of frames to take for the background. If more than 1, they will be averaged and the SD used to check for movement. Default: %(default)s.')
parser.add_argument('--n-SDs', dest='nSds', type=float, default=config['tracker']['nSDs'], help='If the above n-background-frames option is selected, the number of standard deviations to use as threshold for movement. Default: %(default)s.')

parser.add_argument('--clear-borders', dest='clearBorders', action='store_true', default=config['tracker']['clearBorders'], help='Clear the borders of the mask for the detection. Default: %(default)s.')

parser.add_argument('--min-area', dest='minArea', type=int, default=config['mouseArea']['min'], help='The minimum area of the mouse in pixels to be considered valid. Default: %(default)s.')
parser.add_argument('--max-area', dest='maxArea', type=int, default=config['mouseArea']['max'], help='The maximum area of the mouse in pixels to be considered valid. Default: %(default)s.')
parser.add_argument('--n-iter', dest='nIter', type=int, default=config['tracker']['nIter'], help='The number of iterations for the erosion to remove the tail. Default: %(default)s.')
parser.add_argument('--teleportation-threshold', dest='teleportationThreshold', type=int, default=config['tracker']['teleportationThreshold'], help="The number of pixels in either x or y the mouse shouldn't jump by to be considered valid. Default: %(default)s.")

parser.add_argument('--filter-size', dest='oneDKernel', type=int, default=config['analysis']['filterSize'], help='Size in points of the Gaussian kernel filtered used to smooth the trajectory. Set to zero to avoid smoothing. Default: %(default)s.')

parser.add_argument('--roi-center', dest='center', type=coords, nargs=2, default=config['tracker']['roi']['center'], help='Center (in pixels) of the roi for the mouse. No roi if missing. Default: %(default)s.')
parser.add_argument('--roi-radius', dest='radius', type=int, default=config['tracker']['roi']['radius'], help='Radius (in pixels) of the roi for the mouse. No roi if missing. Default: %(default)s.')

parser.add_argument('--plot', action='store_true', default=config['figs']['plot'], help='Whether to display the tracking progress.')
parser.add_argument('--save-graphics', dest='saveGraphs', action='store_true', default=config['figs']['save'], help='Whether to save the plots.')
parser.add_argument('--image-file-format', dest='imgFileFormat', type=str, choices=config['analysis']['imageFormat']['options'], default=config['analysis']['imageFormat']['default'], help='The image format to save the figures in.')
parser.add_argument('--prefix', type=str, help='A prefix to append to the saved figures and data.')

if __name__ == '__main__':
    args = parser.parse_args()
    assert 0 <= args.threshold < 256, "The threshold must be between 0 and 255, got: {}".format(args.threshold) # Avoids list from boundaries in argparse

    def promptDelete(folder):
        msg = 'The folder {} exists, '.format(folder)
        msg += "do you want to delete it ('Y','N')?\n"
        answer = raw_input(msg).upper()
        if answer not in ('Y', 'N'):
            print('{} is not a valid answer'.format(answer))
            answer = promptDelete(folder)
        return True if answer == 'Y' else False
        
    def createDestFolder(srcFolder, prefix):
        destFolder = os.path.join(srcFolder, prefix)
        if os.path.isdir(destFolder):
            if promptDelete(destFolder):
                tmpDest = os.path.join(tempfile.gettempdir(), prefix)
                if os.path.isdir(tmpDest): shutil.rmtree(tmpDest)
                shutil.move(destFolder, tmpDest)
                print('Your folder has been moved to {}, where you can retrive it before it is deleted by a reboot of your machine'\
                .format(tmpDest))
        os.mkdir(destFolder)
        return destFolder

    # Folders and files
    srcFolder = os.path.dirname(args.videoFile)
    vidName = os.path.basename(args.videoFile)
    prefix = None
    if args.saveGraphs:
        if not args.prefix:
            prefix = os.path.splitext(vidName)[0]
    prefix = prefix if prefix is not None else args.prefix
    destFolder = createDestFolder(srcFolder, prefix)
    imgExt = '.'+args.imgFileFormat

    # Time information
    viewer = Viewer(args.videoFile)
    if args.bgTime is None and args.trackFrom is None and args.trackTo is None:
        args.bgTime, args.trackFrom, args.trackTo = viewer.view()
    else:
        args.bgTime = viewer.timeStrToFrameIdx(args.bgTime)
        args.trackFrom = viewer.timeStrToFrameIdx(args.trackFrom)
        args.trackTo = viewer.timeStrToFrameIdx(args.trackTo)

    # ROI
    if args.center and args.radius:
        roi = Circle(args.center, args.radius)
    else:
        roi = None
        
    ############################### TRACKING ########################################
    tracker = Tracker(srcFilePath=args.videoFile, destFilePath=None,
                    threshold=args.threshold, minArea=args.minArea,
                    maxArea=args.maxArea, teleportationThreshold=args.teleportationThreshold,
                    bgStart=args.bgTime, trackFrom=args.trackFrom, trackTo=args.trackTo,
                    nBackgroundFrames=args.nBackgroundFrames, nSds=args.nSds,
                    clearBorders=args.clearBorders, normalise=False,
                    plot=args.plot, fast=config['tracker']['fast'], 
                    extractArena=False)
    positions = tracker.track(roi=roi)

    ################################ ANALYSIS ########################################
    os.chdir(destFolder)
    positions = filterPositions(positions, args.oneDKernel) if args.oneDKernel else positions
    samplingFreq = 1.0/tracker._stream.fps

    # Track
    plotTrack(positions, tracker.bg)
    plt.savefig('mousePath'+imgExt) if args.saveGraphs else plt.show()

    # Angles
    angles = getAngles(positions)
    writeDataList(angles, 'angles.dat')
    plt.figure()
    plotAngles(angles, samplingFreq)
    plt.savefig('angles'+imgExt) if args.saveGraphs else plt.show()

    # Distances
    distances = posToDistances(positions)
    writeDataList(distances, 'distances.dat')
    plt.figure()
    plotDistances(distances, samplingFreq)
    plt.savefig('distances'+imgExt) if args.saveGraphs else plt.show()

    # Integrals
    plt.figure()
    plotIntegrals(angles, samplingFreq)
    plt.savefig('integrals'+imgExt) if args.saveGraphs else plt.show()

    header = ('frameNum', 'centreX', 'centreY', 'width', 'height', 'angle')

    ################################ SAVE DATA AND PARAMS ##########################
    def writeCsv(header, table, dest):
        with open(dest, 'w') as csvFile:
            writer = csv.writer(csvFile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if header:
                writer.writerow(header)
            for row in table:
                writer.writerow(row)
                
    writeCsv(header, positions, 'data.dat')
    paramsHeader = ('param_name', 'param_value')
    params = sorted(vars(args).items())
    writeCsv(paramsHeader, params, 'params.dat')
