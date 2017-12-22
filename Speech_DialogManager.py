from PyQt5.QtCore import (Qt, QObject, pyqtSignal, QThread)
import time

class Speech_DialogManager(QThread):

    updated = pyqtSignal()  # in order to work it has to be defined out of the contructor
    finished = pyqtSignal()  # in order to work it has to be defined out of the contructor

    def __init__(self):
        super().__init__()