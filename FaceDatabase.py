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

import os
import sys

import sqlite3

class FaceDatabase:
    """
    Class that provides an interface for the faces and identities database.

    Attributes:
        
    """
    def __init__(self):
        self.path_to_faces = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Faces/"
        #self.conn = sqlite3.connect(self.path_to_faces + 'faces.db')
        self.model_face_encodings = []

    def retrieve(self):
        #preload faces encodings
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

    # def close(self):
    #     self.conn.close()
