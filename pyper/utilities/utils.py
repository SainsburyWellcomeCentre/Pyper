import sys
from HTMLParser import HTMLParser


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

