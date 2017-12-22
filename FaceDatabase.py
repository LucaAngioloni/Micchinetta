import face_recognition
import cv2
import numpy as np

import os
import sys

class FaceDatabase:
    def __init__(self):
        self.path_to_faces = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Faces/"
        self.model_face_encodings = []

    def retrieve(self):
        self.images = sorted([f for f in os.listdir(self.path_to_faces) if not f.startswith('.')],
                            key=lambda f: f.lower())
        self.names = [os.path.splitext(n)[0] for n in self.images]

        self.model_face_encodings = []
        for image in self.images:
            name_image = face_recognition.load_image_file(self.path_to_faces+image)
            self.model_face_encodings.append(face_recognition.face_encodings(name_image)[0])

    def get_identity(self, face_encoding):
        matches = []

        for i, model_encoding in enumerate(self.model_face_encodings):
            matches.append(face_recognition.compare_faces([model_encoding], face_encoding)[0])

        name = "Unknown"

        for i in range(len(matches)):
            if matches[i]:
                name = self.names[i]

        return name

    def get_image_for_ID(self, id):
        try:
            idx = self.names.index(id)
            return self.path_to_faces + self.images[idx]
        except ValueError:
            return None
