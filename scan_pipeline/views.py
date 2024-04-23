from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import QtGui
from .ui.window import Ui_Form
from pathlib import Path

class Window(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self._setupUI()

    def _setupUI(self):
        self.setupUi(self)