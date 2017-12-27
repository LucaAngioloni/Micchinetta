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

from PyQt5.QtCore import (Qt, QObject, pyqtSignal)
from PyQt5.QtGui import QImage, qRgb, QPixmap
from PyQt5.QtWidgets import (QLabel, QSizePolicy)
#import numpy as np


class VideoWidget(QLabel):
    """
    Custom Widget to show the visual feedback of face recognition.
    Attributes:
        active      Qt Signal emitted every time this view is activated (visible)
        non_active  Qt Signal emitted every time this view is deactivated (non visible)
        V_margin    dimension of right and left margin in window (widget) coordinates for the image
        H_margin    dimension of top and bottom margin in window (widget) coordinates for the image
        h           currentFrame height
        w           currentFrame width
        image       image representing the currentFrame. (Numpy Array)
    """
    active = pyqtSignal() # in order to work it has to be defined out of the contructor
    non_active = pyqtSignal() # in order to work it has to be defined out of the contructor

    def __init__(self, face_recogniser):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.V_margin = 0
        self.H_margin = 0
        self.h = 0
        self.w = 0
        self.image = None
        self.face_recogniser = face_recogniser

        self.face_recogniser.updated.connect(self.new_image_slot, type=Qt.QueuedConnection)
        self.active.connect(self.face_recogniser.loop, type=Qt.QueuedConnection)
        self.non_active.connect(self.face_recogniser.deactivate, type=Qt.QueuedConnection)

    def set_model(self, image):
        """
        Set the reference to the current image.
        Args:
            image     current image of face recognition
        """
        self.image = image
        self.updateView()  # update the view to show the first frame

    def new_image_slot(self):
        """Qt Slot for updated signal of the FaceRecogniser. Called every time a new frame is elaborated"""
        self.image = self.face_recogniser.get_current_frame()
        self.updateView()

    def activate(self):
        """Called upon activation of this view, emits the activated signal so that the Face recognition process can start"""
        self.active.emit()

    def deactivate(self):
        """Called upon deactivation of this view, emits the non_active signal so that the Face recognition process can stop"""
        self.non_active.emit()

    def updateView(self):
        """Update the view converting the current state image (np.ndarray) to an image (QPixmap) and showing it on screen"""
        # All this conversion are not beautiful but necessary...
        if self.image is None:
            return
        mat = self.image
        self.h = mat.shape[0]
        self.w = mat.shape[1]
        qim = self.toQImage(mat)  # first convert to QImage
        qpix = QPixmap.fromImage(qim)  # then convert to QPixmap
        # set the pixmap and resize to fit the widget dimension
        self.setPixmap(qpix.scaled(self.size(), Qt.KeepAspectRatio, Qt.FastTransformation))
        # calculate the margins
        self.V_margin = (self.size().height() - self.pixmap().size().height()) / 2
        self.H_margin = (self.size().width() - self.pixmap().size().width()) / 2

    def toQImage(self, im):
        """
        Utility method to convert a numpy array to a QImage object.
        Args:
            im          numpy array to be converted. It can be a 2D (BW) image or a color image (3 channels + alpha)
        Returns:
            QImage      The image created converting the numpy array
        """
        gray_color_table = [qRgb(i, i, i) for i in range(256)]
        if im is None:
            return QImage()
        if len(im.shape) == 2:  # 1 channel image
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim
        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888)
                return qim
            elif im.shape[2] == 4:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32)
                return qim