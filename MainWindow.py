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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QStackedLayout)
import numpy as np

class MainWindow(QWidget):
    """
    Main window controller
    Attributes:
        videoWidget     Custom widget of type VideoWidget that represents the face recognition view.
        dialogWidget    Custom widget of type DialogWidget that represents the dialog view.
        stackLayout     Qt Layout that contains videoWidget and dialogWidget.
    """
    def __init__(self, videoWidget, dialogWidget):
        super().__init__()
        self.videoWidget = videoWidget
        self.dialogWidget = dialogWidget
        self.init_ui()

    def init_ui(self):
        """Method to initialize the UI: layouts and components"""
        self.setWindowTitle("Michinetta")

        self.stackLayout = QStackedLayout()

        self.stackLayout.addWidget(self.videoWidget)
        self.stackLayout.addWidget(self.dialogWidget)

        self.setLayout(self.stackLayout)
        self.setMinimumSize(800, 600)
        self.show()
        #self.videoWidget.set_model(np.zeros((100,100, 3)))

    def resizeEvent(self, ev):
        """Slot for window resize event (Override)"""
        self.videoWidget.updateView()
        super().resizeEvent(ev)

    def activate_video(self):
        self.dialogWidget.deactivate()
        self.videoWidget.activate()
        self.stackLayout.setCurrentIndex(0)

    def activate_dialog(self):
        self.videoWidget.deactivate()
        self.dialogWidget.activate(self.videoWidget.face_recogniser.currentUser)
        self.stackLayout.setCurrentIndex(1)
