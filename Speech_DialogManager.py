# MIT License

# Copyright (c) 2017 Luca Angioloni and Francesco Pegoraro

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PyQt5.QtCore import (Qt, QObject, pyqtSignal, QThread)
import time

class Speech_DialogManager(QThread):
    """
    Class that provides an interface for the dialog and actions components.

    Attributes:
        
    """
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