"""
Pyper, The command line interface

:author: crousse
"""

import os
import sys
import argparse
import csv
import shutil
import tempfile

from configobj import ConfigObj

from pyper.tracking.tracking import Viewer, Tracker
from pyper.contours.roi import Circle
from pyper.analysis.video_analysis import *


def coords(string):
    try:
        return int(string.strip())
    except:
        raise argparse.ArgumentError('Coordinates must be x, y. Got {}'.format(string))

# CLI
configPath = os.path.expanduser(os.path.normcase('~/.motionTracking.conf'))
config = ConfigObj(configPath, encoding="UTF8", indent_type='    ', unrepr=True,
                   create_empty=True, write_empty_values=True)
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
    assert 0 <= args.threshold < 256, \
        "The threshold must be between " \
        "0 and 255, got: {}".format(args.threshold)  # Avoids list from boundaries in argparse

    def prompt_delete(folder):
        msg = 'The folder {} exists, '.format(folder)
        msg += "do you want to delete it ('Y','N')?\n"
        answer = raw_input(msg).upper()
        if answer not in ('Y', 'N'):
            print('{} is not a valid answer'.format(answer))
            answer = prompt_delete(folder)
        return True if answer == 'Y' else False
        
    def create_dest_folder(src_folder, prefix):
        dest_folder = os.path.join(src_folder, prefix)
        if os.path.isdir(dest_folder):
            if prompt_delete(dest_folder):
                tmp_dest = os.path.join(tempfile.gettempdir(), prefix)
                if os.path.isdir(tmp_dest):
                    shutil.rmtree(tmp_dest)
                shutil.move(dest_folder, tmp_dest)
                print('Your folder has been moved to {}, where you can retrieve it before it is deleted '
                      'by rebooting your machine'.format(tmp_dest))
        os.mkdir(dest_folder)
        return dest_folder

    # Folders and files
    src_folder = os.path.dirname(args.videoFile)
    vid_name = os.path.basename(args.videoFile)
    prefix = None
    if args.saveGraphs and not args.prefix:
        prefix = os.path.splitext(vid_name)[0]
    prefix = prefix if prefix is not None else args.prefix
    dest_folder = create_dest_folder(src_folder, prefix)
    img_ext = '.' + args.imgFileFormat

    # Time information
    viewer = Viewer(args.videoFile)
    if args.bg_time is None and args.track_from is None and args.track_to is None:
        args.bg_time, args.track_from, args.track_to = viewer.view()
    else:
        args.bg_time = viewer.time_str_to_frame_idx(args.bg_time)
        args.track_from = viewer.time_str_to_frame_idx(args.track_from)
        args.track_to = viewer.time_str_to_frame_idx(args.track_to)

    # ROI
    if args.center and args.radius:
        roi = Circle(args.center, args.radius)
    else:
        roi = None
        
    # TRACKING
    tracker = Tracker(srcFilePath=args.videoFile, destFilePath=None,
                      threshold=args.threshold, minArea=args.minArea,
                      maxArea=args.maxArea, teleportationThreshold=args.teleportationThreshold,
                      bgStart=args.bg_time, trackFrom=args.track_from, trackTo=args.track_to,
                      nBackgroundFrames=args.nBackgroundFrames, nSds=args.nSds,
                      clearBorders=args.clearBorders, normalise=False,
                      plot=args.plot, fast=config['tracker']['fast'],
                      extractArena=False)
    positions = tracker.track(roi=roi)

    # ANALYSIS
    os.chdir(dest_folder)
    positions = filter_positions(positions, args.oneDKernel) if args.oneDKernel else positions
    samplingFreq = 1.0/tracker._stream.fps

    plot_track(positions, tracker.bg)
    plt.savefig('mousePath' + img_ext) if args.saveGraphs else plt.show()

    angles = get_angles(positions)
    write_data_list(angles, 'angles.dat')
    plt.figure()
    plot_angles(angles, samplingFreq)
    plt.savefig('angles' + img_ext) if args.saveGraphs else plt.show()

    distances = pos_to_distances(positions)
    write_data_list(distances, 'distances.dat')
    plt.figure()
    plot_distances(distances, samplingFreq)
    plt.savefig('distances' + img_ext) if args.saveGraphs else plt.show()

    plt.figure()
    plot_integrals(angles, samplingFreq)
    plt.savefig('integrals' + img_ext) if args.saveGraphs else plt.show()

    header = ('frameNum', 'centreX', 'centreY', 'width', 'height', 'angle')

    # SAVE DATA AND PARAMS
    def write_csv(header, table, dest):
        with open(dest, 'w') as csvFile:
            writer = csv.writer(csvFile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if header:
                writer.writerow(header)
            for row in table:
                writer.writerow(row)
                
    write_csv(header, positions, 'data.dat')
    params_header = ('param_name', 'param_value')
    params = sorted(vars(args).items())
    write_csv(params_header, params, 'params.dat')
