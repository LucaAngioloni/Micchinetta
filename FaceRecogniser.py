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

import face_recognition
import cv2
import numpy as np
from PyQt5.QtCore import (Qt, QObject, pyqtSignal, QThread)

from FaceDatabase import FaceDatabase


class FaceRecogniser(QThread):
    """
    Thread responsible for background capture and analysis of images from the camera. 
    It performs face detection, embedding extraction and queries the Face Database for recognition.

    Attributes:
        updated             Qt Signal emitted every time a new image is elaborated.
        person_identified   Qt Signal emitted every time a person is identified.
        database            Instance of FaceDatabase.
        currentFrame        Numpy array containing the last elaborated frame.
        active              Boolean status of the recognition progress
        currentUser         Temporary attribute to store the last recognised user.
    """
    updated = pyqtSignal() # in order to work it has to be defined out of the contructor
    person_identified = pyqtSignal() # in order to work it has to be defined out of the contructor

    def __init__(self):
        super().__init__()
        self.database = FaceDatabase()
        self.database.retrieve()

        self.currentFrame = None
        self.active = False
        self.currentUser = None

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
        last_id = ""

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
                    # See if the face is a match for the known face(s)
                    id = self.database.get_identity(face_encoding)
                    name = self.database.get_nickname(id)
                    face_names.append(name)
                    if id != "Unknown" and id == last_id:
                        count = count + 1
                    else:
                        last_id = id
                        count = 0

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
                
                if count > 12:  # Final recognition of a user and send the person_identified signal
                    self.active = False
                    video_capture.release()
                    self.currentUser = last_id
                    self.person_identified.emit()

                self.updated.emit()
