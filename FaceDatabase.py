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
import json

import sqlite3

class FaceDatabase:
    """
    Class that provides an interface for the faces and identities database.

    Attributes:
        path_to_faces           path to the faces images
        model_face_encodings    python dictionary containing a face encoding (value) for each user (key)
        toll                    threshold for face similarity
        conn                    Database connection
    """
    def __init__(self):
        self.path_to_faces = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Faces/"
        self.model_face_encodings = {}
        self.toll = 0.55

    def retrieve(self):
        """Method to pre-load faces encodings (populate the model_face_encodings dictionary)"""
        self.conn = sqlite3.connect(self.path_to_faces + 'faces.db')
        c = self.conn.cursor()
        for row in c.execute('SELECT id, encoding FROM faces'):
            if row is None:
                self.conn.close()
                return
            self.model_face_encodings[row[0]] = np.array(json.loads(row[1]))
        self.conn.close()

    def get_identity(self, face_encoding):
        """
        Method to find the closest match in the faces database for a face_encoding. If none is found under the tollerance, Unknown is returned.

        Args:
            face_encoding    face encoding to match with database identities
        """
        model_encodings = [self.model_face_encodings[k] for k in self.model_face_encodings]
        dists = face_recognition.face_distance(model_encodings, face_encoding)

        min_val = np.min(dists)
        min_id = np.argmin(dists)

        if min_val <= self.toll:
            return list(self.model_face_encodings.keys())[min_id]
        else:
            return "Unknown"

    def get_image_for_ID(self, id):
        """
        Method to find and return the image path relative to a user's identity id.

        Args:
            id    the user's identity
        """
        self.conn = sqlite3.connect(self.path_to_faces + 'faces.db')
        c = self.conn.cursor()
        c.execute('SELECT im_path FROM faces WHERE id = ?', (id,))
        ret = c.fetchone()
        if ret is None:
            self.conn.close()
            return None
        self.conn.close()
        return self.path_to_faces + ret[0]

    def get_nickname(self, id):
        """
        Method to find and return the nikname relative to a user's identity id.

        Args:
            id    the user's identity
        """
        self.conn = sqlite3.connect(self.path_to_faces + 'faces.db')
        c = self.conn.cursor()
        c.execute('SELECT nikname FROM faces WHERE id = ?', (id,))
        ret = c.fetchone()
        if ret is None:
            self.conn.close()
            return None
        self.conn.close()
        return ret[0]
