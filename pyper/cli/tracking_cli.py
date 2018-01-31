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

from pyper.tracking.tracking import Tracker
from pyper.tracking.viewer import Viewer
from pyper.contours.roi import Circle
from pyper.analysis.video_analysis import *
from pyper.config import conf


def coords(string):
    try:
        return int(string.strip())
    except:
        raise argparse.ArgumentError('Coordinates must be x, y. Got {}'.format(string))


def get_parser():
    config = conf.config

    parser = argparse.ArgumentParser(prog=sys.argv[0])  # TODO: do parser groups

    parser.add_argument('video_file', type=str, nargs='?', default=config['tests']['default_video'],
                        help='Path (relative or absolute) of the video file to process.')

    parser.add_argument('-b', '--background-time', dest='bg_time', metavar='MM:SS',  # TODO: do frame indexed variant
                        type=str, help='Time in mm:ss format for the background frame.')
    parser.add_argument('-f', '--track-from', dest='track_from', metavar='MM:SS',  # TODO: do frame indexed variant
                        type=str, help='Time in mm:ss format for the tracking start.')
    parser.add_argument('-t', '--track-to', dest='track_to', metavar='MM:SS',  # TODO: do frame indexed variant
                        type=str, help='Time in mm:ss format for the tracking end.')
    parser.add_argument('--n-background-frames', dest='n_background_frames', type=int,
                        default=config['tracker']['sd_mode']['n_background_frames'],
                        help='The number of frames to take for the background.'
                             ' If more than 1, they will be averaged and the SD used to check for movement.'
                             ' Default: %(default)s.')
    parser.add_argument('--n-SDs', dest='n_sds', type=float, default=config['tracker']['sd_mode']['n_sds'],
                        help='If the above n-background-frames option is selected,'
                             ' the number of standard deviations to use as threshold for movement. Default: %(default)s.')

    parser.add_argument('--clear-borders', dest='clear_borders', action='store_true',
                        default=config['tracker']['checkboxes']['clear_borders'],
                        help='Clear the borders of the mask for the detection. Default: %(default)s.')
    # TODO: add normalise

    parser.add_argument('--threshold', type=int, default=config['tracker']['detection']['threshold'],
                        help='The brightness level to threshold the image for feature detection. Default: %(default)s.')
    parser.add_argument('--min-area', dest='min_area', type=int, default=config['tracker']['detection']['min_area'],
                        help='The minimum area of the object in pixels to be considered valid. Default: %(default)s.')
    parser.add_argument('--max-area', dest='max_area', type=int, default=config['tracker']['detection']['max_area'],
                        help='The maximum area of the object in pixels to be considered valid. Default: %(default)s.')
    parser.add_argument('--teleportation-threshold', dest='teleportation_threshold', type=int,
                        default=config['tracker']['detection']['teleportation_threshold'],
                        help="The number of pixels in either x or y the mouse shouldn't jump by to be considered valid."
                             " Default: %(default)s.")
    # parser.add_argument('--n-iter', dest='n_iter', type=int, default=config['tracker']['n_iter'],
    #                     help='The number of iterations for the erosion to remove the tail. Default: %(default)s.')  # FIXME: unused

    parser.add_argument('--filter-size', dest='one_d_kernel', type=int, default=config['analysis']['filter_size'],
                        help='Size in points of the Gaussian kernel filtered used to smooth the trajectory.'
                             ' Set to zero to avoid smoothing. Default: %(default)s.')

    parser.add_argument('--roi-center', dest='center', type=coords, nargs=2, default=config['tracker']['roi']['center'],
                        help='Center (in pixels) of the roi for the mouse. No roi if missing. Default: %(default)s.')
    parser.add_argument('--roi-radius', dest='radius', type=int, default=config['tracker']['roi']['radius'],
                        help='Radius (in pixels) of the roi for the mouse. No roi if missing. Default: %(default)s.')

    parser.add_argument('--plot', action='store_true', default=config['figures']['plot'],
                        help='Whether to display the tracking progress.')
    parser.add_argument('--save-graphics', dest='save_graphs', action='store_true', default=config['figures']['save'],
                        help='Whether to save the plots.')
    parser.add_argument('--image-file-format', dest='img_file_format', type=str,
                        choices=config['analysis']['image_format']['options'],
                        default=config['analysis']['image_format']['default'],
                        help='The image format to save the figures in.')
    parser.add_argument('--prefix', type=str, help='A prefix to append to the saved figures and data.')
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    assert 0 <= args.threshold < 256,\
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
    src_folder = os.path.dirname(args.video_file)
    vid_name = os.path.basename(args.video_file)
    prefix = None
    if args.save_graphs and not args.prefix:
        prefix = os.path.splitext(vid_name)[0]
    prefix = prefix if prefix is not None else args.prefix
    dest_folder = create_dest_folder(src_folder, prefix)
    img_ext = '.' + args.img_file_format

    # Time information
    viewer = Viewer(args.video_file)
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
    tracker = Tracker(src_file_path=args.video_file, dest_file_path=None,
                      threshold=args.threshold, min_area=args.min_area,
                      max_area=args.max_area, teleportation_threshold=args.teleportation_threshold,
                      bg_start=args.bg_time, track_from=args.track_from, track_to=args.track_to,
                      n_background_frames=args.n_background_frames, n_sds=args.n_sds,
                      clear_borders=args.clear_borders, normalise=config['tracker']['checkboxes']['normalise'],
                      plot=args.plot, fast=config['tracker']['checkboxes']['fast'],
                      extract_arena=False)
    positions = tracker.track(roi=roi)

    # ANALYSIS
    os.chdir(dest_folder)
    positions = filter_positions(positions, args.one_d_kernel) if args.one_d_kernel else positions
    samplingFreq = 1.0/tracker._stream.fps

    plot_track(positions, tracker.bg)
    plt.savefig('mousePath' + img_ext) if args.save_graphs else plt.show()

    angles = get_angles(positions)
    write_data_list(angles, 'angles.dat')
    plt.figure()
    plot_angles(angles, samplingFreq)
    plt.savefig('angles' + img_ext) if args.save_graphs else plt.show()

    distances = pos_to_distances(positions)
    write_data_list(distances, 'distances.dat')
    plt.figure()
    plot_distances(distances, samplingFreq)
    plt.savefig('distances' + img_ext) if args.save_graphs else plt.show()

    plt.figure()
    plot_integrals(angles, samplingFreq)
    plt.savefig('integrals' + img_ext) if args.save_graphs else plt.show()

    header = ('frame_num', 'centre_x', 'centre_y', 'width', 'height', 'angle')

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
