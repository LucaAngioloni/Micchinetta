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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if qdark_present:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    face_recon = FaceRecogniser()
    video = VideoWidget(face_recon)
    dialog = DialogWidget()

    window = MainWindow(video, dialog)  # The view controller / view (GUI)

    video.face_recogniser.updated.connect(video.new_image_slot, type=Qt.QueuedConnection)
    video.active.connect(video.face_recogniser.loop, type=Qt.QueuedConnection)
    video.non_active.connect(video.face_recogniser.deactivate, type=Qt.QueuedConnection)

    window.activate_video()
    sys.exit(app.exec_())