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

"""
============
MICChinetta
============

An application interface using both face and speech recognition to achieve a transaction between the user and a vending machine.
"""

import sys
import time

from PyQt5.QtWidgets import QApplication  # pip install PyQt5
from PyQt5.QtCore import (Qt, QObject, pyqtSignal)

qdark_present = True
try:
    import qdarkstyle  # Qt styling package, pip install qdarkstyle
except ImportError:
    qdark_present = False

from MainWindow import MainWindow
from VideoWidget import VideoWidget
from DialogWidget import DialogWidget
from FaceRecogniser import FaceRecogniser
from Speech_DialogManager import Speech_DialogManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if qdark_present:  # load qdarkstyle if present
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    face_recon = FaceRecogniser()
    speechManager = Speech_DialogManager()
    video = VideoWidget(face_recon)
    dialog = DialogWidget(speechManager)

    window = MainWindow(video, dialog)  # The view controller / view (GUI)

    # Qt Signals and slots connection
    video.face_recogniser.person_identified.connect(window.activate_dialog, type=Qt.QueuedConnection)
    dialog.speech_dialog_manager.finished.connect(window.activate_video, type=Qt.QueuedConnection)

    # Starts with the Face Recognition
    window.activate_video()

    sys.exit(app.exec_())