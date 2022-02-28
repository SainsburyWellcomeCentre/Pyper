import os

import numpy as np
from scipy.spatial import distance

from pyper.tracking.tracking_results import TrackingResults


class MultiResults(object):
    def __init__(self, params, thresholding_params):
        self.results = [TrackingResults() for i in range(thresholding_params.n_structures_max)]
        self.params = params
        self.thresholding_params = thresholding_params

    # def append_default_measure(self):

    def __len__(self):
        return len(self.results[0])

    def save(self, struct_name='', dest_folder=None):
        if dest_folder is None:
            dest_folder = os.path.dirname(self.params.dest_path)
        base_name = os.path.splitext(os.path.basename(self.params.dest_path))[0]
        for i, res in enumerate(self.results):
            f_name = "{}_structure_{}_instance_{}.fthr".format(base_name, struct_name, i)
            dest_path = os.path.join(dest_folder, f_name)
            df = res.as_df()
            df.reset_index().to_feather(dest_path)  # TEST:

    def reset(self):
        for res in self.results:
            res.reset()

    def set_start_time(self, start_time):
        for res in self.results:
            res.start_time = start_time

    def last_pos_is_default(self):
        return np.array([res.last_pos_is_default() for res in self.results]).all()

    def append_defaults(self):
        for res in self.results:
            res.append_defaults()

    def get_prev_pos(self, skip_defaults=False):
        return [res.get_last_position(skip_defaults=skip_defaults) for res in self.results]

    def match_positions(self, new_pos):
        """
        Match results at rounds n and n-1 by position, i.e. if
        we have 3 structures [A, B, C] and 3 new [C', A', B'], we use their
        respective positions to put [A', B', C'] into the list containing [A, B, 'C] in
        that order.
        If number of structures is different from previous round,
        handle merge and put NaN to dropped structure

        :param np.array new_pos: The positions at round n
        :return: matched_idx
        """
        if self.thresholding_params.n_structures_max == 1:  # Don't match 1 (speedup)
            return np.array([[0, 0]])
        if self.has_non_default_position():
            prev_pos = np.array(self.get_prev_pos(skip_defaults=True))  # Walk backwards to first non default position
        else:
            return np.tile(np.arange(len(new_pos)), (2, 1)).T
        if new_pos.size == 0:
            new_pos = np.full(prev_pos.shape, np.NaN, prev_pos.dtype)
            print("Setting default to {}".format(new_pos))
        n_active_pos_prev = len(prev_pos[~np.isnan(prev_pos)]) / 2  # /2 because 1 values per coordinate
        merging = n_active_pos_prev > len(new_pos)

        dist_mat = distance.cdist(prev_pos, new_pos, 'euclidean')

        src_idx = []
        dst_idx = []
        smallest_distances = []
        for i in range(min(len(prev_pos), len(new_pos))):
            tmp_dst_idx = np.unravel_index(dist_mat.argmin(), dist_mat.shape)  # TODO: numpy notation
            src_idx.append(tmp_dst_idx[0])
            dst_idx.append(tmp_dst_idx[1])
            smallest_distances.append(dist_mat[tmp_dst_idx])
            dist_mat[tmp_dst_idx[0], :] = np.inf
            dist_mat[:, tmp_dst_idx[1]] = np.inf

        matched_idx = np.column_stack((src_idx, dst_idx))
        if merging:
            pass  # TODO: put as NaN when no src_idx

        return matched_idx

    def multi_update(self, arena, contours, measures):
        """
        :param Roi arena:
        :param MultiContour contours:
        :param list measures:
        :return:
        """
        areas = contours.areas
        new_pos = np.array(contours.centres)
        if new_pos.size == 0:
            return  # FIXME:
        matched_indexes = self.match_positions(new_pos)
        for i, matched_idx in enumerate(matched_indexes):
            src_idx = matched_idx[0]
            dst_idx = matched_idx[1]
            if np.isnan(dst_idx):
                continue  # Leave as default
            pos = new_pos[dst_idx]
            if arena is None:
                arena_distances = (None, None)
            else:
                arena_distances = (arena.dist_from_centre(pos), arena.dist_from_border(pos))
            self.results[src_idx].update(pos, areas[i], measures[i], arena_distances)
            self.results[src_idx].last_contour = contours[i]  # FIXME: check match index
        # TODO: Check that sizes match with previous round

    def get_row(self, idx):
        for i, res in enumerate(self.results):
            if i == 0:
                row = res.get_row(idx)
            else:
                row.extend(res.get_row(idx)[2:])
        return row

    def get_positions(self):
        return np.stack([res.positions for res in self.results])

    def get_times(self):
        return np.stack([res.times for res in self.results])

    def plotting_positions(self):
        pos = self.get_positions()
        non_default_pos_idx = np.column_stack([res.non_default_pos_idx() for res in self.results])
        non_default_pos_idx = non_default_pos_idx.all(axis=1)
        trimmed_pos = pos[:, non_default_pos_idx, :]
        return trimmed_pos

    def check_teleportation(self, frame, mask, current_frame_idx):
        """
        Check if the specimen moved too much, which would indicate an issue with the tracking
        notably the fitting in the past. If so, call self._stream.stopRecording() and raise
        EOFError.

        :param video_frame.Frame frame: The current frame (to be saved for troubleshooting if teleportation occurred)
        :param mask: The binary mask of the current frame\
         (to be saved for troubleshooting if teleportation occurred)
        :type mask: video_frame.Frame

        :raises: EOFError if the specimen teleported
        """
        if not self.has_non_default_position():  # No tracking yet
            return
        teleporters = [False] * len(self.results)
        for i, res in enumerate(self.results):
            last_vector = res.get_last_movement_vector()
            if last_vector is None:
                return
            if (last_vector > self.params.max_movement).any():
                print('structure {} teleported'.format(i))
                teleporters[i] = True
        if teleporters.count(True) == len(self.results):  # all
            mask.save('teleporting_silhouette.tif')  # Used for debugging
            frame.save('teleporting_frame.tif')
            err_msg = 'Frame: {}, specimen teleported from {} to {}\n' \
                .format(current_frame_idx, *self.results[0].get_last_pos_pair())  # TODO: manage all results ??
            err_msg += 'Please see teleporting_silhouette.tif and teleporting_frame.tif for debugging'
            return err_msg

    def has_non_default_position(self):
        return np.array([res.has_non_default_position() for res in self.results]).all()
