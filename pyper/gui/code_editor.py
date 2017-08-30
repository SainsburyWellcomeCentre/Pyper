import imp
import os

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QFileDialog

from pyper.gui.tabs_interfaces import TRACKER_CLASSES


class EditorIface(QObject):
    def __init__(self, app, context, parent):
        """
        :param app: The QT application
        :param context:
        :param parent: the parent window
        """
        QObject.__init__(self, parent)
        self.app = app  # necessary to avoid QPixmap bug: Must construct a QGuiApplication before
        self.win = parent
        self.ctx = context

        self.src_path = None

        self.plugin_dir = os.getenv('HOME')  # FIXME:
        self.plugins = TRACKER_CLASSES  # FIXME: see if can improve

    @pyqtSlot(result=str)
    def open_plugin_code(self):
        diag = QFileDialog()
        path = diag.getOpenFileName(parent=diag,
                                    caption='Open file',
                                    directory=self.plugin_dir,
                                    filter="*.py")
        src_path = path[0]
        if src_path:
            self.src_path = src_path
            with open(src_path, 'r') as in_file:
                code = in_file.read()
            return code
        else:
            return ''

    @pyqtSlot(str)
    def save_plugin_code(self, src_code):
        diag = QFileDialog()
        path = diag.getSaveFileName(parent=diag,
                                    caption='Save file',
                                    directory=self.plugin_dir,
                                    filter="*.py")
        dest_path = path[0]
        if not dest_path.endswith('.py'):
            dest_path += '.py'
        if dest_path:
            with open(dest_path, 'w') as out_file:
                out_file.write(src_code)

    @pyqtSlot(str, result=str)
    def export_code_to_plugins(self, code):
        code_lines = code.split("\n")
        if [l.startswith('class') for l in code_lines].count(True) > 1:  # We don't know how to handle more than one
            return ''
        for l in code_lines:
            if l.startswith('class'):
                class_name = l.split(' ')[1]
                class_name = class_name.split('(')[0].strip()
                break
        else:
            return ''

        plugin = imp.new_module(class_name)
        exec code in plugin.__dict__
        cls = getattr(plugin, class_name)
        self.plugins[class_name] = cls
        return class_name

    @pyqtSlot(result=str)
    def load_plugin_template(self):
        with open(os.path.join(self.plugin_dir, 'template.py'), 'r') as in_file:
            template_code = in_file.read()
        return template_code