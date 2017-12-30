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

from PyQt5.QtCore import (Qt, QObject, pyqtSignal, QThread)
import time
import speech_recognition as sr

from Bot import Bot

class Speech_DialogManager(QThread):
    """
    Class that provides an interface for the dialog and actions components.

    Attributes:
        
    """
    updated = pyqtSignal(object, object)  # in order to work it has to be defined out of the contructor
    finished = pyqtSignal()  # in order to work it has to be defined out of the contructor

    def __init__(self):
        super().__init__()
        self.active = False

        self.recognizer = sr.Recognizer()
        self.products = {"lay's": 1, "arachidi": 2, "coca-cola": 1.60, "acqua": 1, "birra": 2} # da prendere con apis
        self.bot = Bot(self.products)
        self.username = ''

    def set_username(self, name):
        self.username = name
        self.bot.set_user_name(self.username)

    def record_and_understand(self):
        with sr.Microphone() as source:
            print("Say something!")
            audio = self.recognizer.listen(source)
        print("stopped recording")
        # Speech recognition using Google Speech Recognition
        try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
            said = self.recognizer.recognize_google(audio, language='it')
            print("You said: " + said)
            return said
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def write(self):
        usersays = input("Say something!")
        return usersays

    def loop(self):
        #self.bot.say("ok")
        self.start()

    def deactivate(self):
        self.active = False
        if self.isRunning():
            self.terminate()

    def run(self):
        self.active = True
        self.bot.sayhi()

        while self.active:
            user_says = self.write() # da sostituire con record_and_understand
            self.updated.emit(user_says, 0)
            val, reply, bill = self.bot.reply(user_says)
            self.updated.emit(reply, bill)
            if val:
                print("fine")
                self.finished.emit()

        #     pass
        # self.updated.emit()
