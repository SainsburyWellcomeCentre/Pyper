import imp
import os

import sys
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QFileDialog

from pyper.gui.tabs_interfaces import TRACKER_CLASSES

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    from pyper.utilities.utils import strip_html_tags

    PYGMENTS_IMPORTED = True
except ImportError:
    PYGMENTS_IMPORTED = False


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

        self.plugin_dir = os.path.abspath("config/plugins/")  # FIXME: improve (currently dependant on start folder)
        self.plugins = TRACKER_CLASSES
        # self.scrape_plugins_dir()

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

    def get_class_name(self, code):
        code_lines = code.split("\n")
        if [l.startswith('class') for l in code_lines].count(True) > 1:  # We don't know how to handle more than one
            return ''
        for l in code_lines:
            if l.startswith('class'):
                class_name = l.split(' ')[1]
                class_name = class_name.split('(')[0].strip()
                return class_name
        else:
            return ''

    def code_to_plugin(self, class_name, code):
        plugin = imp.new_module(class_name)
        try:
            exec code in plugin.__dict__
        except SyntaxError as err:
            print("Could not load plugin {}, because of syntax error\n\t{}".format(class_name, err))
            raise SyntaxError  # TODO: specific exception
        cls = getattr(plugin, class_name)
        sys.modules[class_name.lower()] = plugin
        exec("from {} import {} as cls".format(class_name.lower(), class_name))
        self.plugins[class_name] = cls

    @pyqtSlot()
    def scrape_plugins_dir(self):
        for fname in os.listdir(self.plugin_dir):
            if not fname.endswith('.py'):
                continue
            if fname in ("__init__.py", "template.py"):
                continue
            file_path = os.path.join(self.plugin_dir, fname)
            with open(file_path, 'r') as module_file:
                code = module_file.read()
            class_name = self.get_class_name(code)
            if not class_name:
                continue
            else:
                try:
                    self.code_to_plugin(class_name, code)
                except SyntaxError:
                    continue
                algo_menu = self.win.findChild(QObject, "trackingAlgorithmMenu")
                algo_menu.setProperty("lastAddedEndtry", class_name)

    @pyqtSlot(str, result=str)
    def export_code_to_plugins(self, code):
        if PYGMENTS_IMPORTED:
            code = strip_html_tags(code)
        class_name = self.get_class_name(code)
        if not class_name:
            return ''
        else:
            try:
                self.code_to_plugin(class_name, code)
            except SyntaxError:
                return ''
            return class_name

    @pyqtSlot(result=str)
    def load_plugin_template(self):
        with open(os.path.join(self.plugin_dir, 'template.py'), 'r') as in_file:
            template_code = in_file.read()
        if PYGMENTS_IMPORTED:
            template_code = self.highlight_code(template_code)
        return template_code

    @pyqtSlot(str, result=str)
    def highlight_code(self, code):
        return highlight(code, PythonLexer(), HtmlFormatter(full=True, style='native'))

