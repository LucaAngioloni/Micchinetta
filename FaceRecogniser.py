import face_recognition
import cv2
import numpy as np
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
        self.active = False
        self.currentUser = None

    def get_current_frame(self):
        return self.currentFrame

    def deactivate(self):
        self.active = False
        if self.isRunning():
            self.terminate()

    def loop(self):
        self.currentUser = None
        self.start()

    def get_single_face(self, face_locations):
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
        self.active = True
        video_capture = cv2.VideoCapture(0)
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []

        count = 0
        last_name = ""

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
                    name = self.database.get_identity(face_encoding)
                    face_names.append(name)
                    if name != "Unknown" and name == last_name:
                        count = count + 1
                    else:
                        last_name = name
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

                # Display the resulting image
                self.currentFrame = frame

                if count > 10:
                    self.currentFrame = cv2.copyMakeBorder(frame, top=20, bottom=20, left=20, right=20, borderType= cv2.BORDER_CONSTANT, value=[0,220,0] )
                
                if count > 12:
                    self.active = False
                    video_capture.release()
                    self.currentUser = last_name
                    self.person_identified.emit()

                self.updated.emit()
