import os
import subprocess
import tempfile

from pyper.exceptions.exceptions import PyperError


class VideoConversionError(PyperError):
    pass


class VideoCompressionError(PyperError):
    pass


def ffmpeg_recode_times(src_video_file_path, new_rate, dest_video_file_path=None, verbose=False):
    """
    :param str src_video_file_path:
    :param float new_rate: The new frame rate to be encoded as
    :param str dest_video_file_path:  If ommited, overwites the source video
    :return:
    """

    # tmp_file = os.path.join(tempfile.gettempdir(), "raw.h264")
    tmp_file = os.path.join(os.path.normpath(os.path.expanduser('~/Downloads/')), "raw.h264")
    tmp_file = tmp_file.replace('\\', '/')
    #  First, copy the video to a raw bitstream format.
    # For H265
    # "ffmpeg -i input.mp4 -map 0:v -c:v copy -bsf:v hevc_mp4toannexb raw.h265"
    # cmd = "ffmpeg -i {infile} -map 0:v -c:v copy -bsf:v mpeg2video {tmpfile}"\
    cmd = "ffmpeg -y -i {infile} -map 0:v -c:v copy -bsf:v h264_mp4toannexb {tmpfile}"\
        .format(infile=src_video_file_path, tmpfile=tmp_file)
    if verbose:
        print(cmd)
    try:
        subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        pass
        # raise VideoConversionError(str(e))

    # Then generate new timestamps while muxing to a container:
    if dest_video_file_path is None:
        dest_video_file_path = src_video_file_path
    cmd = "ffmpeg -y -fflags +genpts -r {rate} -i {tmp} -c:v copy {dest}"\
        .format(rate=new_rate, tmp=tmp_file, dest=dest_video_file_path)
    if verbose:
        print(cmd)
    try:
        subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        pass
        # raise VideoConversionError(str(e))


def ffmpeg_compress(src_video_file_path, dest_video_file_path, compression_ratio,
                    grain=False, compatibility=False, max_tries=3, overwrite=False, verbose=False):
    """
    Uses the shell to compress the source file with FFMPEG in H264 using the specified CRF
    the pixel format is hard coded to 420 for max compatibility


    :param str src_video_file_path: The path to the source video (has to be supported by your FFMPEG install)
    :param str dest_video_file_path: The path to save the file to
    :param int compression_ratio: The CRF (Constant Rate Factor) value to use for compression
    :param bool grain: Whether to preserve the grain of the video in H264 encoding
    :param int max_tries: Maximum number of times this command will be automatically retries before raising an exception
    defaults to 3.
    :param bool overwrite: Whether to overwrite destination file if it already exists
    :param bool verbose: Show command line being executed
    :return:
    """""
    overwrite_option = '-y ' if overwrite else ''
    grain_option = '-tune grain' if grain else ''
    compatibility_option = ' -profile:v high' if compatibility else ''
    cmd = 'ffmpeg -loglevel 16 {overwrite_option}-i "{in_file_path}" -c:v libx264'\
          ' -crf {compression_ratio} {grain_opt} -pix_fmt yuv420p'\
          '{compatibility_opt}'\
          ' -c:a copy "{compressed_file_path}"'\
        .format(overwrite_option=overwrite_option,
                in_file_path=src_video_file_path, compression_ratio=compression_ratio, grain_opt=grain_option,
                compatibility_opt=compatibility_option, compressed_file_path=dest_video_file_path)
    if verbose:
        print(cmd)
    attempts = 0
    processed = False
    while not processed:
        if attempts < max_tries:
            try:
                result = subprocess.check_output(cmd, shell=True)
                processed = True
            except subprocess.CalledProcessError as e:
                print('Video conversion ERROR: "{}"'.format(e))
                attempts += 1
        else:
            raise VideoCompressionError('Max conversion attempts exceeded')
