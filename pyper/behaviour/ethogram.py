import os
import sys
from collections import namedtuple

import numpy as np
import pandas as pd
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog
from scipy.io import loadmat

from pyper.exceptions.exceptions import PyperError
from pyper.utilities.utils import find_range_starts, find_range_ends

DATA_TYPES = "Data (*.mat *.npy *.csv)"


class Ethogram:
    def __init__(self, length=0):
        self.behaviours = pd.DataFrame({'name': ['None', 'Idle'],
                                        'num_id': [0, 1],
                                        'colour': ['#353535', '#808080'],
                                        'shortcut': ['0', 'Ctrl+i']})
        self.data = np.array(length, dtype=np.int64)
        self.current_behaviour = 0  # no behaviour
        self.previous_behaviour = 0
        self.first_behaviour_frame = 0

    def create_empty(self, n_frames):
        self.data = np.zeros(round(n_frames), dtype=np.int64)
        self.current_behaviour = 0
        self.behaviours = pd.DataFrame({'name': ['None', 'Idle'],
                                        'num_id': [0, 1],
                                        'colour': ['#353535', '#808080'],
                                        'shortcut': ['0', 'Ctrl+i']})
        behaviour_strings = [self.bhv_to_str(bhv) for bhv in self.behaviours.itertuples(index=False)]
        return behaviour_strings

    @staticmethod
    def bhv_to_str(bhv):
        colour = bhv.colour
        q_col = QColor(colour)
        rgb_color = [c / 255 for c in q_col.getRgb()]
        return "{name};{num_id};{colour};{shortcut}".format(name=bhv.name, num_id=bhv.num_id,
                                                            colour=rgb_color, shortcut=bhv.shortcut)

    def _get_max_numerical_shortcut(self):
        shortcuts = self.behaviours['shortcut']
        max_number = shortcuts[~shortcuts.str.contains('Ctrl')].max()  # TODO: should check for other modifiers
        if np.isnan(max_number):
            max_number = 0
        return int(max_number)

    def add_behaviour(self):
        _name = 'Undefined'
        _id = 2 * self.behaviours['num_id'].max()
        _colour = 'red'
        _shortcut = str(self._get_max_numerical_shortcut() + 1)
        bhv = {'name': [_name],
               'num_id': [_id],
               'colour': [_colour],
               'shortcut': [_shortcut]
               }
        row = pd.DataFrame.from_records(bhv)
        self.behaviours = pd.concat((self.behaviours, row), ignore_index=True)
        for _row in row.itertuples(index=False):  # FIXME: dirty conversion
            tpl = _row
        return self.bhv_to_str(tpl)

    def remove_behaviour(self, bhv_name):
        bhv = self.behaviours[self.behaviours['name'] == bhv_name]
        # remove from table
        self.behaviours = self.behaviours.drop(bhv.index)
        # reset that bhv to default in vector
        self.data[self.data == bhv.numerical_id] = self.behaviours['num_id'][self.behaviours['name'] == 'None']

    def switch_state(self, bhv_id, current_frame_idx):  # FIXME: when stops without close
        update = False
        if bhv_id == self.current_behaviour:  # ending behaviour
            self.data[self.first_behaviour_frame:current_frame_idx] = bhv_id
            self.current_behaviour = self.previous_behaviour
            self.first_behaviour_frame = current_frame_idx
            update = True
        else:  # starting new behaviour
            self.data[self.first_behaviour_frame:current_frame_idx] = self.current_behaviour  # close other first
            self.previous_behaviour = self.current_behaviour
            self.current_behaviour = bhv_id
            self.first_behaviour_frame = current_frame_idx
        return update

    def close_behaviour(self, frame_id):
        self.switch_state(self.current_behaviour, frame_id)

    def data_str(self):
        return ";".join([str(d) for d in self.data])

    # def items(self):
    #     return [(bhv.name, bhv.numerical_id) for bhv in self.behaviours.values()]

    def load_data(self):
        src_path = self._create_load_dialog()
        if src_path:
            extension = os.path.splitext(src_path)[-1]
            if extension == '.npy':
                self.data = np.load(src_path)
            elif extension == '.mat':
                self.data = loadmat(src_path)  # TEST:
            elif extension == '.csv':
                self.data = np.genfromtext(src_path, delimiter=',')  # OPTIMISE: pandas
            else:
                raise PyperError("Unknown extension: {}".format(extension))
            self.current_behaviour = 0
            return True
        else:
            return False

    def save(self):
        dest_path = self._create_save_dialog()
        if dest_path:
            extension = os.path.splitext(dest_path)[-1]
            if extension == '.npy':
                np.save(dest_path, self.data)
            elif extension == '.csv':
                df = self.behaviour_bouts_to_df()
                df.to_csv(dest_path)
            else:
                raise NotImplementedError("Please implement methods for other extensions")

    def behaviour_bouts_to_df(self):
        table = []
        for bhv_name, num_id in self.behaviours[['name', 'num_id']].itertuples(index=False):
            bhv_mask = self.data == num_id
            bhv_starts = np.where(find_range_starts(bhv_mask))[0]
            bhv_ends = np.where(find_range_ends(bhv_mask))[0]
            for start, end in zip(bhv_starts, bhv_ends):
                table.append([bhv_name, num_id, start, end])
        df = pd.DataFrame(table, columns=['behaviour_name', 'behaviour_id', 'start_frame', 'end_frame'])
        return df

    def _create_load_dialog(self):
        diag = QFileDialog()
        if sys.platform == 'win32':  # avoids bug with windows COM object init failed
            opt = QFileDialog.Options(QFileDialog.DontUseNativeDialog)
        else:
            opt = QFileDialog.Options()
        src_path = diag.getOpenFileName(parent=diag,
                                        caption='Choose data file',
                                        directory=os.path.expanduser('~'),
                                        filter=DATA_TYPES,
                                        initialFilter="Data (*.npy)",
                                        options=opt)
        src_path = src_path[0]
        return src_path

    def _create_save_dialog(self):
        diag = QFileDialog()
        if sys.platform == 'win32':  # avoids bug with windows COM object init failed
            opt = QFileDialog.Options(QFileDialog.DontUseNativeDialog)
        else:
            opt = QFileDialog.Options()
        dest_path = diag.getSaveFileName(parent=diag,
                                         caption='Choose data file',
                                         directory=os.path.expanduser('~'),
                                         filter=DATA_TYPES,
                                         initialFilter="Data (*.npy)",
                                         options=opt)
        dest_path = dest_path[0]
        return dest_path
