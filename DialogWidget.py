from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
	QStackedLayout, QTableWidget, QPlainTextEdit, QSizePolicy)
from PyQt5.QtCore import (Qt, QObject, pyqtSignal)
from PyQt5.QtGui import QImage, qRgb, QPixmap

from FaceDatabase import FaceDatabase

class DialogWidget(QWidget):
    """
    Dialog window controller
    Attributes:
    """

    active = pyqtSignal() # in order to work it has to be defined out of the contructor
    non_active = pyqtSignal() # in order to work it has to be defined out of the contructor

    def __init__(self, speech_dialog_manager):
        super().__init__()
        self.speech_dialog_manager = speech_dialog_manager
        #interface
        self.image = QLabel()
        self.name = QLabel()
        self.dialog = QPlainTextEdit()
        self.table = QTableWidget()


        image_v_box = QVBoxLayout()
        image_v_box.addWidget(self.image)
        image_v_box.addWidget(self.name)

        img_dialog_h_box = QHBoxLayout()
        img_dialog_h_box.addLayout(image_v_box)
        img_dialog_h_box.addWidget(self.dialog)

        layout = QVBoxLayout()
        layout.addLayout(img_dialog_h_box)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.image.setAlignment(Qt.AlignCenter)
        self.name.setAlignment(Qt.AlignCenter)
        #self.image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image.resize(200, 400)

        self.speech_dialog_manager.updated.connect(self.update_dialog, type=Qt.QueuedConnection)
        self.active.connect(self.speech_dialog_manager.loop, type=Qt.QueuedConnection)
        self.non_active.connect(self.speech_dialog_manager.deactivate, type=Qt.QueuedConnection)


    def deactivate(self):
        self.non_active.emit()

    def activate(self, user):
        db = FaceDatabase()
        db.retrieve()

        img = db.get_image_for_ID(user)
        self.name.setText(user)
        if img is not None:
            qpix = QPixmap(img)

            self.image.setPixmap(qpix.scaled(self.image.size(), Qt.KeepAspectRatio, Qt.FastTransformation))
        else:
            self.image.setText("None")

    
    def update_dialog(self):
        # slot called whenever Speech_DialogManager has updates. Update the view
        pass


