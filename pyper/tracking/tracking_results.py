import csv
import numpy as np
from time import time


class TrackingResults(object):
    def __init__(self):
        self.times = []
        self.positions = []  # TODO: see if use array for efficiency in has_non_default_position
        self.measures = []
        self.areas = []  # The area of the tracked object
        self.distances_from_arena = []
        self.in_tracking_roi = []

        self.start_time = None

        self.default_pos = (-1, -1)
        self.only_defaults = True
        self.default_measure = float('NaN')
        self.default_area = 0.
        self.default_distance_from_arena = (float('NaN'), float('NaN'))
        self.default_in_tracking_roi = False

    def _reset(self):
        self.times = []
        self.positions = []
        self.measures = []
        self.areas = []  # The area of the tracked object
        self.distances_from_arena = []
        self.in_tracking_roi = []

    def reset(self):
        self._reset()

    def trim_positions(self):  # OPTIMISE:
        # pos = np.int32(self.positions)
        # pos = pos[pos != self.default_pos]
        return [p for p in self.positions if p != self.default_pos]

    def plot_positions(self):
        pos = self.trim_positions()  # FIXME: put trimming as option
        return np.int32([pos])

    def __len__(self):
        return len(self.positions)

    def _get_title(self):
        return ["frame", "time", "x", "y", "area", "x to arena", "y to arena", "measure", "in trakcing roi"]

    def get_title(self):
        return self._get_title()

    def to_csv(self, dest):  # FIXME: add title
        with open(dest, 'w') as out_file:
            writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.get_title())
            for i in range(len(self)):
                writer.writerow(self.get_row(i))

    def _get_row(self, idx):
        row = [idx]
        row.append("{0:.3f}".format(self.times[idx]))
        row.extend(["{0:.2f}".format(p) for p in self.positions[idx]])
        row.append("{0:.2f}".format(self.areas[idx]))
        row.extend(["{0:.1f}".format(p) for p in self.distances_from_arena[idx]])
        row.append("{0:.3f}".format(self.measures[idx]))
        row.append(self.in_tracking_roi[idx])
        return row

    def get_row(self, idx):
        return self._get_row(idx)

    def get_frame_results(self):
        return self.get_last_position(), self.get_last_dist_from_arena_pair()

    def get_last_position(self):
        if len(self) > 0:
            last_pos = tuple(self.positions[-1])
            return last_pos
        else:
            return None  # TODO: see if prefer exception

    def last_pos_is_default(self):
        return self.get_last_position() == self.default_pos

    def repeat_last_position(self):
        self.positions.append(self.positions[-1])

    def overwrite_last_pos(self, position):
        self.positions[-1] = position
        if position != self.default_pos:
            self.only_defaults = False

    def overwrite_last_measure(self, measure):
        self.measures[-1] = measure

    def overwrite_last_area(self, area):
        self.areas[-1] = area

    def overwrite_last_dist_from_arena(self, distances):
        self.distances_from_arena[-1] = distances

    def overwrite_last_in_tracking_roi(self, val):
        """

        :param bool val:
        :return:
        """
        self.in_tracking_roi[-1] = val

    def overwrite_last_time(self, t):
        self.times[-1] = t

    def get_last_movement_vector(self):
        if len(self.positions) < 2:
            return
        last_vector = np.abs(np.array(self.positions[-1]) - np.array(self.positions[-2]))  # OPTIMISE:
        return last_vector

    def get_last_pos_pair(self):
        return self.positions[-2:]

    def get_last_dist_from_arena_pair(self):
        return self.distances_from_arena[-1]

    def get_last_in_tracking_roi(self):
        return self.in_tracking_roi[-1]

    def get_last_time(self):
        return self.times[-1]

    def append_default_measure(self):
        self.measures.append(self.default_measure)

    def append_default_area(self):
        self.areas.append(self.default_area)

    def append_default_pos(self):
        self.positions.append(self.default_pos)

    def append_default_dist_from_arena(self):
        self.distances_from_arena.append(self.default_distance_from_arena)

    def append_default_in_tracking_roi(self):
        self.in_tracking_roi.append(self.default_in_tracking_roi)

    def append_default_time(self):
        if self.start_time is not None:
            self.times.append(time() - self.start_time)
        else:
            self.times.append(0.0)
            self.start_time = time()

    def _append_defaults(self):
        self.append_default_pos()
        self.append_default_area()
        self.append_default_measure()
        self.append_default_dist_from_arena()
        self.append_default_in_tracking_roi()
        self.append_default_time()

    def append_defaults(self):
        self._append_defaults()

    def repeat_last(self):
        if len(self) > 0:
            self.repeat_last_position()
            self.repeat_last_measure()
            self.repeat_last_area()
            self.repeat_last_distance_from_arena()
            self.repeat_last_in_tracking_roi()
            self.append_default_time()  # Time is always current
        else:
            self.append_defaults()

    def repeat_last_measure(self):
        self.measures.append(self.measures[-1])

    def repeat_last_area(self):
        self.areas.append(self.areas[-1])

    def repeat_last_distance_from_arena(self):
        self.distances_from_arena.append(self.distances_from_arena[-1])  # FIXME: copy list

    def repeat_last_in_tracking_roi(self):
        self.in_tracking_roi.append(self.in_tracking_roi[-1])

    def update(self, position, area, measure, distances):  # TODO: see if add in_tracking_roi
        self.overwrite_last_pos(position)
        self.overwrite_last_measure(measure)
        self.overwrite_last_area(area)
        if distances[0] is not None:
            self.overwrite_last_dist_from_arena(distances)

    def has_non_default_position(self):
        return not self.only_defaults

