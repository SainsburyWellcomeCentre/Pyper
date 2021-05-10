from time import time

import numpy as np
import pandas as pd


class TrackingResults(object):
    def __init__(self):
        self.times = []
        self.xs = []
        self.ys = []
        self.measures = []
        self.areas = []  # The area of the tracked object
        self.distances_from_arena_xs = []
        self.distances_from_arena_ys = []
        self.in_tracking_roi = []

        self.start_time = None

        self.default_pos = -1
        self.only_defaults = True
        self.default_measure = float('NaN')
        self.default_area = 0.
        self.default_distance_from_arena = float('NaN')
        self.default_in_tracking_roi = False

    def _reset(self):
        self.times = []
        self.xs = []
        self.ys = []
        self.measures = []
        self.areas = []
        self.distances_from_arena_xs = []
        self.distances_from_arena_ys = []
        self.in_tracking_roi = []

    def reset(self):
        self._reset()

    @property
    def positions(self):
        return np.array((self.xs, self.ys), dtype=np.int32).T

    def trim_positions(self):
        return self.positions[self.non_default_pos_idx()]

    def non_default_pos_idx(self):
        return np.logical_not((self.positions == self.default_pos).all(axis=1))

    def plotting_positions(self):
        # pos = self.trim_positions()  # TODO: put trimming as option
        # return np.int32([pos])
        return self.trim_positions()

    def __len__(self):
        return len(self.xs)

    @property
    def header(self):
        return ["frame", "time", "x", "y", "area", "x to arena", "y to arena", "measure", "in tracking roi"]

    def as_df(self):
        return pd.DataFrame(data=zip(np.arange(len(self)), self.times,  # FIXME: replace arange by index
                                     self.xs, self.ys, self.areas,
                                     self.distances_from_arena_xs, self.distances_from_arena_ys,
                                     self.measures, self.in_tracking_roi),
                            columns=self.header)

    def to_csv(self, dest):
        self.as_df().to_csv(dest)
        # with open(dest, 'w') as out_file:
        #     writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #     writer.writerow(self.header)
        #     for i in range(len(self)):
        #         writer.writerow(self.get_row(i))

    def get_row(self, idx):
        row = [idx]
        row.append("{0:.3f}".format(self.times[idx]))
        row.append("{0:.2f}".format(self.xs[idx]))
        row.append("{0:.2f}".format(self.ys[idx]))
        row.append("{0:.2f}".format(self.areas[idx]))
        row.extend("{0:.1f}".format(self.distances_from_arena_xs[idx]))
        row.extend("{0:.1f}".format(self.distances_from_arena_ys[idx]))
        row.append("{0:.3f}".format(self.measures[idx]))
        row.append(self.in_tracking_roi[idx])
        return row

    def get_frame_results(self):
        return self.get_last_position(), self.get_last_dist_from_arena_pair()

    def get_last_position(self, skip_defaults=False):
        if len(self) > 0:
            if not skip_defaults:
                return self.xs[-1], self.ys[-1]  # TODO: check if needs parentheses
            else:
                for i in range(1, len(self)):
                    pos = self.xs[-i], self.ys[-i]
                    if pos != (-1, -1):
                        return pos
        else:
            return None  # TODO: see if prefer exception

    def last_pos_is_default(self):
        return self.get_last_position() == (self.default_pos, self.default_pos)

    def repeat_last_position(self):
        self.xs.append(self.xs[-1])
        self.ys.append(self.ys[-1])

    def overwrite_last_pos(self, position):
        self.xs[-1] = position[0]
        self.ys[-1] = position[1]
        if (position != self.default_pos).all():
            self.only_defaults = False  # REFACTOR: replace by

    def overwrite_last_measure(self, measure):
        self.measures[-1] = measure

    def overwrite_last_area(self, area):
        self.areas[-1] = area

    def overwrite_last_dist_from_arena(self, distances):
        self.distances_from_arena_xs[-1] = distances[0]
        self.distances_from_arena_ys[-1] = distances[1]

    def overwrite_last_in_tracking_roi(self, val):
        """

        :param bool val:
        :return:
        """
        self.in_tracking_roi[-1] = val

    def overwrite_last_time(self, t):
        self.times[-1] = t

    def get_last_movement_vector(self):
        if len(self.xs) < 2:
            return
        last_vector = np.abs(np.array(self.positions[-1]) - np.array(self.positions[-2]))  # OPTIMISE:
        return last_vector

    def get_last_pos_pair(self):
        return (self.xs[-2], self.ys[-2]), (self.xs[-1], self.ys[-1])

    def get_last_dist_from_arena_pair(self):
        return self.distances_from_arena_xs[-1], self.distances_from_arena_ys[-1]

    def get_last_in_tracking_roi(self):
        return self.in_tracking_roi[-1]

    def get_last_time(self):
        return self.times[-1]

    def append_default_measure(self):
        self.measures.append(self.default_measure)

    def append_default_area(self):
        self.areas.append(self.default_area)

    def append_default_pos(self):
        self.xs.append(self.default_pos)
        self.ys.append(self.default_pos)

    def append_default_dist_from_arena(self):
        self.distances_from_arena_xs.append(self.default_distance_from_arena)
        self.distances_from_arena_ys.append(self.default_distance_from_arena)

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
        self.distances_from_arena_xs.append(self.distances_from_arena_xs[-1])  # FIXME: copy list
        self.distances_from_arena_ys.append(self.distances_from_arena_ys[-1])  # FIXME: copy list

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
