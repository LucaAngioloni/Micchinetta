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
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QTableView, QSizePolicy, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtCore import Qt, QFileInfo, QUrl, QFile
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import face_recognition
import numpy as np
import json
import uuid
from VideoWidget import VideoWidget

path_to_faces = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Faces/"
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName(path_to_faces + 'faces.db')

import cv2
from PyQt5.QtCore import (Qt, QObject, pyqtSignal, QThread)

from FaceDatabase import FaceDatabase


class FaceRecogniser(QThread):
    updated = pyqtSignal() # in order to work it has to be defined out of the contructor
    person_identified = pyqtSignal() # in order to work it has to be defined out of the contructor

    def __init__(self):
        super().__init__()
        self.database = FaceDatabase()
        self.database.retrieve()

        self.currentFrame = None
        self.userImage = None
        self.active = False
        self.currentUser = None
        self.toll = 0.5

    def get_user_image(self):
        return cv2.cvtColor(self.userImage, cv2.COLOR_RGB2BGR)

    def get_current_frame(self):
        """Getter for the currentFrame attribute"""
        return self.currentFrame

    def deactivate(self):
        """Method called to stop and deactivate the face recognition Thread"""
        self.active = False
        if self.isRunning():
            self.terminate()

    def loop(self):
        """Method called to initialize and start the face recognition Thread"""
        self.currentUser = None
        self.start()

    def get_single_face(self, face_locations):
        """
        Method that accepts multiple face locations and returns the location of the biggest surface location.

        Args:
            face_locations     List containing detected faces locations (each of them is a list containig the top, right, bottom, left values)
        """
        selected = 0
        max_area = 0
        for i, face in enumerate(face_locations):
            top, right, bottom, left = face
            area = abs(right-left) * abs(bottom-top)
            if area > max_area:
                max_area = area
                selected = i
        return [face_locations[selected]]

    def run(self):
        """Main loop of this Thread"""
        self.active = True
        video_capture = cv2.VideoCapture(0)
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []

        count = 0
        last_enc = None
        cane = 0

        while self.active:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            if ret:
                frame = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),1)
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(small_frame)

                if face_locations:
                    face_locations = self.get_single_face(face_locations)
                else:
                    count = 0

                face_encodings = face_recognition.face_encodings(small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                
                    if last_enc is None:
                        last_enc = np.copy(face_encoding)
                    else:
                        if face_recognition.face_distance([last_enc], face_encoding)[0] <= self.toll:
                            count = count + 1
                        else:
                            last_enc = face_encoding
                            count = 0
                    face_names.append("")
                    
                self.userImage = frame.copy()
                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Store the current image
                self.currentFrame = frame

                if count > 10:  # A user has been recognised, activation of acceptance graphical effect (green borders)
                    self.currentFrame = cv2.copyMakeBorder(frame, top=20, bottom=20, left=20, right=20, borderType= cv2.BORDER_CONSTANT, value=[0,220,0] )
                    print("found 0")
                
                if count > 12:  # Final recognition of a user and send the person_identified signal
                    print("found")
                    self.active = False
                    video_capture.release()
                    self.currentUser = last_enc
                    self.person_identified.emit()

                self.updated.emit()


class GetPicture(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Database Manager - Take Photo'
        self.setFixedSize(600,400)

        self.face_recognizer = FaceRecogniser()
        self.video_widget = VideoWidget(self.face_recognizer)
        h = QHBoxLayout()
        h.addWidget(self.video_widget)
        self.setLayout(h)

    def activate(self):
        self.show()
        self.video_widget.activate()

    def deactivate(self):
        self.hide()
        self.video_widget.deactivate()


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
 
    new_id = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.title = 'Database Manager - Add'
        self.width = 320
        self.height = 320
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)

        self.photo_button = QPushButton("Take Photo")
        self.label = CustomLabel('Drop here', self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.photo_button)
        self.setLayout(layout)
        self.show()
        self.photo_button.clicked.connect(self.take_photo)
        self.picture = GetPicture()
        self.picture.face_recognizer.person_identified.connect(self.photo_taken)

    def take_photo(self):
        self.picture.activate()

    def photo_taken(self):
        self.picture.deactivate()
        encoding = self.picture.face_recognizer.currentUser
        d = {'Name': "", 'Surname': "", 'nikname': "", 'mail': "",  'password': ""}
        dialog = DataDialog(d)
        ret = dialog.exec_()

        for key in d:
            d[key] = dialog.le_dict[key].text()

        if ret is 1:  # accepted
            d['encoding'] = json.dumps(encoding.tolist())
            d['id'] = str(uuid.uuid1())
            d['im_path'] = d['id'] + ".png"
            im_path = path_to_faces + d['im_path']
            image_to_save = self.picture.face_recognizer.get_user_image()
            cv2.imwrite(im_path, image_to_save)

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
        try:
            name_image = face_recognition.load_image_file(e.mimeData().urls()[0].toLocalFile())
            encoding = face_recognition.face_encodings(name_image)[0]
        except IndexError:
            print("The image has no faces in it, or a face can't be found")
            msgBox = QMessageBox()
            msgBox.setText("The image has no faces in it, or a face can't be found");
            msgBox.exec_();
            return
        # finally:
        #     print("Unknown Error")
        #     return

        d = {'Name': "", 'Surname': "", 'nikname': "", 'mail': "",  'password': ""}
        dialog = DataDialog(d)
        ret = dialog.exec_()

        for key in d:
            d[key] = dialog.le_dict[key].text()

        if ret is 1:  # accepted
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
    ex.new_id.connect(ew.update_model)
    sys.exit(app.exec_())
    db.close()