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

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QTableView, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtCore import Qt, QFileInfo, QUrl, QFile
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import face_recognition
import numpy as np
import json
import uuid

path_to_faces = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Faces/"
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName(path_to_faces + 'faces.db')

class EditWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.title = 'Database Manager - Edit'
        self.vLayout = QVBoxLayout()
        self.model = QSqlTableModel(self, db)
        self.model.setTable('faces')
        self.model.select()
        self.table = QTableView(self)
        self.table.setModel(self.model)
        self.table.hideColumn(0)
        self.table.hideColumn(7)
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.delete_row)
        self.vLayout.addWidget(self.table)
        self.vLayout.addWidget(self.deleteButton)
        self.setLayout(self.vLayout)
        self.setFixedSize(600,400)
        self.show()

    def delete_row(self):
        idxs = self.table.selectionModel().selectedIndexes()
        if len(idxs) > 0:
            self.model.removeRows(idxs[0].row(), 1)
            self.model.select()

    def update_model(self):
        self.model.select()

class DataDialog(QDialog):
    
    def __init__(self, d):
        super().__init__()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.vLayout = QVBoxLayout()

        self.le_dict = {}

        for key in d:
            h = QHBoxLayout()
            h.addWidget(QLabel(key))
            qe = QLineEdit()
            self.le_dict[key] = qe
            h.addWidget(qe)
            self.vLayout.addLayout(h)

        self.vLayout.addWidget(self.buttonBox)

        self.setLayout(self.vLayout)
        
 
class AddWindow(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Database Manager - Add'
        self.width = 320
        self.height = 320
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)
 
        self.label = CustomLabel('Drop here', self)
        self.label.setGeometry(0, 0, self.width, self.height)
        self.label.setAlignment(Qt.AlignCenter)
        self.show()
 
class CustomLabel(QLabel):

    new_id = pyqtSignal()
 
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
 
    def dragEnterEvent(self, e):
        if len(e.mimeData().urls()) > 0 and e.mimeData().urls()[0].isLocalFile():
            qi = QFileInfo(e.mimeData().urls()[0].toLocalFile())
            ext = qi.suffix()
            if ext == "jpg" or ext == "jpeg" or ext == "png" or ext == "JPG" or ext == "PNG":
                e.accept()
            else:
                e.ignore()
        else:
            e.ignore()
 
    def dropEvent(self, e):
        print("Dropped")
        print(e.mimeData().urls()[0])

        d = {'Name': "", 'Surname': "", 'nikname': "", 'mail': "",  'password': ""}
        dialog = DataDialog(d)
        ret = dialog.exec_()

        for key in d:
            d[key] = dialog.le_dict[key].text()

        if ret is 1:  # accepted
            name_image = face_recognition.load_image_file(e.mimeData().urls()[0].toLocalFile())
            encoding = face_recognition.face_encodings(name_image)[0]
            d['encoding'] = json.dumps(encoding.tolist())
            qi = QFileInfo(e.mimeData().urls()[0].toLocalFile())
            d['id'] = str(uuid.uuid1())
            d['im_path'] = d['id'] + qi.fileName()
            im_path = path_to_faces + d['im_path']
            QFile.copy(e.mimeData().urls()[0].toLocalFile(), im_path)

            query = QSqlQuery()
            query.prepare("INSERT into faces values(:id, :Name, :Surname, :nikname, :mail, :password, :im_path, :encoding)")
            query.bindValue(":id", d['id'])
            query.bindValue(":Name", d['Name'])
            query.bindValue(":Surname", d['Surname'])
            query.bindValue(":nikname", d['nikname'])
            query.bindValue(":mail", d['mail'])
            query.bindValue(":password", d['password'])
            query.bindValue(":im_path", d['im_path'])
            query.bindValue(":encoding", d['encoding'])
            query.exec_()

            self.new_id.emit()
 
if __name__ == '__main__':
    db.open()
    app = QApplication(sys.argv)
    ex = AddWindow()
    ew = EditWindow()
    ex.label.new_id.connect(ew.update_model)
    sys.exit(app.exec_())
    db.close()