import face_recognition
import cv2
import numpy as np
from PyQt5.QtCore import (Qt, QObject, pyqtSignal, QThread)
import time

class LoopThread(QThread):
    
    done = pyqtSignal()

    def __init__(self, mfe, n, ):
        super().__init__()
        self.model_face_encodings = mfe
        self.names = n
        self.active = False


    def run(self):
        self.active = True
        video_capture = cv2.VideoCapture(0)
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while self.active:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(small_frame)
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = []

                    for i, model_encoding in enumerate(self.model_face_encodings):
                        matches.append(face_recognition.compare_faces([model_encoding], face_encoding)[0])

                    name = "Unknown"

                    for i in range(len(matches)):
                        if matches[i]:
                            name = self.names[i]

                    face_names.append(name)


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
                self.done.emit()
        

class FaceRecogniser(QObject):

    updated = pyqtSignal() # in order to work it has to be defined out of the contructor

    def __init__(self):
        super().__init__()
        #sobstitute this with real databesa query
        self.names = ["Luca", "Pego", "Paola", "Roberto", "Miner"]
        self.images = ["Faces/luca1.jpg", "Faces/pego1.jpg", "Faces/Paola Censini.jpg", "Faces/Roberto Pegoraro.jpg", "Faces/Alessandro Minervini.jpg"]
        self.model_face_encodings = []
        for image in self.images:
            name_image = face_recognition.load_image_file(image)
            self.model_face_encodings.append(face_recognition.face_encodings(name_image)[0])

        self.currentFrame = None
        self.active = False
        self.thread = LoopThread(self.model_face_encodings, self.names)
        self.thread.done.connect(self.update_frame)

    def get_current_frame(self):
        return self.currentFrame

    def deactivate(self):
        self.active = False
        self.thread.terminate()
        self.thread = LoopThread(self.model_face_encodings, self.names)
        self.thread.done.connect(self.update_frame)

    def loop(self):
        self.thread.start()

    def update_frame(self):
        self.currentFrame = self.thread.currentFrame
        self.updated.emit()