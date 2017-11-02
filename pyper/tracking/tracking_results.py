import csv
import numpy as np


class TrackingResults(object):
    def __init__(self):
        self.positions = []  # TODO: see if use array for efficiency in has_non_default_position
        self.measures = []
        self.areas = []  # The area of the tracked object
        self.distances_from_arena = []

        self.default_pos = (-1, -1)
        self.only_defaults = True
        self.default_measure = float('NaN')
        self.default_area = 0.
        self.default_distance_from_arena = (float('NaN'), float('NaN'))

    def reset(self):
        self.positions = []
        self.measures = []
        self.areas = []  # The area of the tracked object
        self.distances_from_arena = []

    def trim_positions(self):  # OPTIMISE:
        # pos = np.int32(self.positions)
        # pos = pos[pos != self.default_pos]
        return [p for p in self.positions if p != self.default_pos]

    def plot_positions(self):
        pos = self.trim_positions()  # FIXME: put trimming as option
        return np.int32([pos])

    def __len__(self):
        return len(self.positions)

    def to_csv(self, dest):
        with open(dest, 'w') as out_file:
            writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(len(self)):
                writer.writerow(self.get_row(i))

    def get_row(self, idx):
        row = [idx]
        row.extend(self.positions[idx])
        row.append(self.areas[idx])
        row.extend(self.distances_from_arena[idx])
        row.append(self.measures[idx])
        return row

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

    def get_last_movement_vector(self):
        if len(self.positions) < 2:
            return
        last_vector = np.abs(np.array(self.positions[-1]) - np.array(self.positions[-2]))  # OPTIMISE:
        return last_vector

    def get_last_pos_pair(self):
        return self.positions[-2:]

    def get_last_dist_from_arena_pair(self):
        return self.distances_from_arena[-1]

    def append_default_measure(self):
        self.measures.append(self.default_measure)

    def append_default_area(self):
        self.areas.append(self.default_area)

    def append_default_pos(self):
        self.positions.append(self.default_pos)

    def append_default_dist_from_arena(self):
        self.distances_from_arena.append(self.default_distance_from_arena)

    def append_defaults(self):
        self.append_default_pos()
        self.append_default_area()
        self.append_default_measure()
        self.append_default_dist_from_arena()

    def repeat_last(self):
        if len(self) > 0:
            self.repeat_last_position()
            self.repeat_last_measure()
            self.repeat_last_area()
            self.repeat_last_distance_from_arena()
        else:
            self.append_defaults()

    def repeat_last_measure(self):
        self.measures.append(self.measures[-1])

    def repeat_last_area(self):
        self.areas.append(self.areas[-1])

    def repeat_last_distance_from_arena(self):
        self.distances_from_arena.append(self.distances_from_arena[-1])

    def update(self, position, area, measure, distances):
        self.overwrite_last_pos(position)
        self.overwrite_last_measure(measure)
        self.overwrite_last_area(area)
        if distances[0] is not None:
            self.overwrite_last_dist_from_arena(distances)

    def has_non_default_position(self):
        return not self.only_defaults

