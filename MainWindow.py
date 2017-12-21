from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QStackedLayout)
import numpy as np

class MainWindow(QWidget):
    """
    Main window controller
    Attributes:
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
        self.setMinimumSize(600, 500)
        self.show()
        self.videoWidget.set_model(np.zeros((100,100, 3)))

    def resizeEvent(self, ev):
        """Slot for window resize event (Override)"""
        self.videoWidget.updateView()
        super().resizeEvent(ev)

    def activate_video(self):
        #self.dialogWidget.deactivate()
        self.videoWidget.activate()
        self.stackLayout.setCurrentIndex(0)

    def activate_dialog(self):
        self.videoWidget.deactivate()
        #self.dialogWidget.activate()
        self.stackLayout.setCurrentIndex(1)
