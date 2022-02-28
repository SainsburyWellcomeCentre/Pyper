import os
import time
import platform

import cv2
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QMessageBox

try:
    from HTMLParser import HTMLParser
    from StringIO import StringIO
    PYTHON_VERSION = 2
except ImportError:
    from html.parser import HTMLParser
    from io import StringIO
    PYTHON_VERSION = 3


colors = {'w': (255, 255, 255),
          'r': (0, 0, 255),
          'g': (0, 255, 0),
          'b': (255, 0, 0),
          'y': (0, 255, 255),
          'c': (255, 255, 0),
          'm': (255, 0, 255)}


def prompt_save(msg, detailed_msg):
    msg_box = QMessageBox()
    # msg_box.setWindowTitle()
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setText(msg)
    msg_box.setDetailedText(detailed_msg)
    msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard)
    msg_box.setDefaultButton(QMessageBox.Save)
    ret_val = msg_box.exec()
    return ret_val == QMessageBox.Save


def display_warning(err, message, modal=True):
    msg_box = QMessageBox()
    msg_box.setWindowTitle('WARNING')
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText('{}: {}'.format(message, str(err)))
    if modal:
        msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        ret_val = msg_box.exec()
        return ret_val
    else:
        msg_box.setStandardButtons(QMessageBox.NoButton)
        QTimer.singleShot(1500, msg_box.accept)
        msg_box.exec_()


class HtmlStripper(HTMLParser):
    """
    Inspired from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    """
    def __init__(self):
        if PYTHON_VERSION == 3:
            super().__init__()
        self.reset()
        if PYTHON_VERSION == 3:
            self.strict = False
            self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        data = self.text.getvalue().splitlines(keepends=True)
        data = data[3:]
        return "".join(data)


def strip_html_tags(html):
    stripper = HtmlStripper()
    stripper.feed(html)
    stripped_text = stripper.get_data()
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
