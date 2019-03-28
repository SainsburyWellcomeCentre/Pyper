import os
import sys
import time
import platform

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
import cv2


def spin_progress_bar(val):
    """
    Spins the progress bar based on the modulo of val

    :param val: The value of the current progress
    """
    modulo = val % 4
    if modulo == 0:
        sys.stdout.write('\b/')
    elif modulo == 1:
        sys.stdout.write('\b-')
    elif modulo == 2:
        sys.stdout.write('\b\\')
    elif modulo == 3:
        sys.stdout.write('\b|')
    sys.stdout.flush()


class HtmlStripper(HTMLParser):
    """
    Inspired from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    """
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, data):
        if "p, li { white-space: pre-wrap; }" in data:  # skip css tags
            return
        self.fed.append(data)

    def handle_entityref(self, name):
        if name == "quot":
            self.fed.append('"')
        else:
            print(name)

    def strip(self):
        return ''.join(self.fed)


def strip_html_tags(html):
    stripper = HtmlStripper()
    stripper.feed(html)
    stripped_text = stripper.strip()
    return stripped_text


def write_structure_not_found_msg(img, img_size, frame_idx):
    """
    Write an error message on the image supplied as argument. The operation is performed in place

    :param int frame_idx: The frame at which the structure cannot be found
    :param img: The source image to write onto
    :param tuple img_size: The size of the source image
    """
    line1 = "No contour found at frame: {}".format(frame_idx)
    line2 = "Please check your parameters"
    line3 = "And ensure specimen is there"
    x = int(50)
    y = int(img_size[0] / 2)
    y_spacing = 40
    font_color = (255, 255, 0)  # yellow
    font_size = 0.75  # percent
    font_type = int(2)
    cv2.putText(img, line1, (x, y), font_type, font_size, font_color)
    y += y_spacing
    cv2.putText(img, line2, (x, y), font_type, font_size, font_color)
    y += y_spacing
    cv2.putText(img, line3, (x, y), font_type, font_size, font_color)


def write_structure_size_incorrect_msg(img, img_size, msg):
    x = int(50)
    y_spacing = 40
    y = int(img_size[0] / 2) - y_spacing
    font_color = (255, 255, 0)  # yellow
    font_size = 0.75  # percent
    font_type = int(2)
    cv2.putText(img, msg, (x, y), font_type, font_size, font_color)


def qurl_to_str(url):  # FIXME: extract to helper module
    url = url.replace("PyQt5.QtCore.QUrl(u", "")
    url = url.strip(")\\'")
    return url


def check_fps(prev_time):
    """
    Prints the number of frames per second
    using the time elapsed since prevTime.

    :param prev_time:
    :type prev_time: time object
    :returns: The new time
    :rtype: time object
    """
    fps = 1 / (time.time() - prev_time)
    print("{} fps".format(fps))
    return time.time()


def un_file(file_path):
    """

    :param str file_path:
    :return:
    """
    if "file://" in file_path:  # Added by QDialog
        file_path = file_path.replace("file://", "")
    if platform.system().lower().startswith('win'):
        if file_path.startswith('/'):
            file_path = file_path[1:]
        file_path = os.path.normpath(file_path)
    return file_path
