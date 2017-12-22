from PyQt5.QtCore import (Qt, QObject, pyqtSignal, QThread)
import time

class Speech_DialogManager(QThread):

    updated = pyqtSignal()  # in order to work it has to be defined out of the contructor
    finished = pyqtSignal()  # in order to work it has to be defined out of the contructor

    def __init__(self):
        super().__init__()
        self.active = False

    def loop(self):
        self.start()

    def deactivate(self):
        self.active = False
        if self.isRunning():
            self.terminate()

    def run(self):
        self.active = True
        # while self.active:
        #     pass
        # self.updated.emit()
        # self.finished.emit()