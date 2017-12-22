from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QStackedLayout)
from PyQt5.QtCore import (Qt, QObject, pyqtSignal)


class DialogWidget(QWidget):
    """
    Dialog window controller
    Attributes:
    """
    def __init__(self, speech_dialog_manager):
        super().__init__()
        self.speech_dialog_manager = speech_dialog_manager