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

from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
	QStackedLayout, QTableWidget, QPlainTextEdit, QSizePolicy, QHeaderView, QTableWidgetItem)
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

        self.dialog.setReadOnly(True)
        self.table.setColumnCount(2);
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['prodotto', 'prezzo'])

        self.list_products = {"lay's": 1, "arachidi": 2, "coca-cola": 1.60, "acqua": 1, "birra": 2} # da prendere con apis



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
        self.dialog.clear()
        self.clear_table()
        db = FaceDatabase()

        img = db.get_image_for_ID(user)

        self.speech_dialog_manager.set_username(db.get_nickname(user));

        self.name.setText(db.get_nickname(user))
        if img is not None:
            qpix = QPixmap(img)

            self.image.setPixmap(qpix.scaled(self.image.size(), Qt.KeepAspectRatio, Qt.FastTransformation))
        else:
            self.image.setText("None")
        self.active.emit()

    def clear_table(self):
        while (self.table.rowCount() > 0):
            self.table.removeRow(0)
        self.table.setRowCount(0);

    def update_bill(self, bill):
        self.clear_table()
        for product in bill:

            if bill[product] > 0:
                price = float("{0:.2f}".format(bill[product]*self.list_products[product]))
                string_prod = str(product) + ' ' + 'X' + str(bill[product])
                rowPosition = self.table.rowCount()
                self.table.insertRow(rowPosition)
                self.table.setItem(rowPosition , 0, QTableWidgetItem(string_prod))
                self.table.setItem(rowPosition , 1, QTableWidgetItem(str(price)))

    # slot called whenever Speech_DialogManager has updates. Update the view
    def update_dialog(self, phrase, bill):
        if bill is not 0:
            print("whay!!!")
            print("bill")
            print(bill)
            self.update_bill(bill)
        self.dialog.appendPlainText(phrase)
        self.dialog.appendPlainText('\n')




