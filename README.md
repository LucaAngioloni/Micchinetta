# Micchinetta

![logo_micchinetta.jpg](./Images/logo_micchinetta.jpg)

## Assignment
Deploy an application interface using both face and speech recognition to achieve a transaction between the user and a vending machine. 
With a webcam, the system should recognize known people. After the recognition, the application must start a conversation-like dialogue with the user:
- **Micchinetta**: Good morning Andy, what do you need?
- **Andy**: I would like three beers and a box of chips, thank you.
- **Micchinetta**: Ok, it's three beers and a box of chips for € 3,80. Ok?
- **Andy**: Ok!

## Goals
1. Recognize people from a set of known faces
2. Sustain a simple conversation with the user to understand his needs
3. Use existing web API, provided by MICC, for transactions and accountability

## Technologies
- The interface is developed with the PyQT Framework using Python.
- Face recognition makes use of a [Python package](https://github.com/ageitgey/face_recognition) and OpenCV for some elaborations and tasks.
- Speech recognition uses a [library](https://pypi.python.org/pypi/SpeechRecognition/) based on Google Cloud APIs.
- The app, to be able to speak, will use this other [Python package](https://pypi.python.org/pypi/pyttsx).
- The Identities along with the face descriptors are maintained in an SQLite database

The system must be connected to the internet to be able to use Google APIs and internal MICC APIs for accountability.
Moreover, the software, to run a simple conversation, will need some capabilities in natural language processing. Many NLP software packages exist, but not many support Italian language along the English language. [TreeTagger](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) is the software chosen.

All of this software components have a significant computational cost and will require a decent machine to run on.

## Interface and Description
To provide a visual feedback to the user, the system implements a simple interface.

The user will find the application in recognition state, with the interface showing a live view of the scene. Approaching the device, the user will appear on the screen and the recognition will start.

![Recognition.png](./Images/Recognition.png)

If recognized (matched with one of the known faces) the system gives a visual feedback of the successful recognition:

![Recognition_feedback.png](./Images/Recognition_feedback.png)

If multiple faces are present int the scene, the closest (biggest) one is used for identity recognition.

The application will then change state, entering the conversation state represented below:

![Conversation.png](./Images/Conversation.png)

As soon as the user is recognized, his reference image from the database will be showed along the matched identity and the conversation shall begin. If the identity matched is wrong, the user can tell the system during the conversation and the system will apologize and retry the recognition.

While speaking, the conversation and the “bill” will be displayed and updated.
If the user agrees to the final bill, the machine will commit the transaction and will change its state to idle.

----------------

Along the main app, an other utility app has been developed to help this system admins to manage the Faces database.
The script `DatabaseManager.py` starts this graphical application that allows to add, remove and modify users identities (and te credentials for the Transactions APIs).

![Database_Manager.png](./Images/Database_Manager.png)

## Usability Tests

## Requirements
| Software                                                    | Version        | Required |
| ------------------------------------------------------------|:--------------:| --------:|
| **Python**                                                  |     >= 3.5     |    Yes   |
| **Qt**                                                      |    >= 5.9.1    |    Yes   |
| **PyQt5** (Python Package)                                  |    >= 5.9.1    |    Yes   |
| **Numpy** (Python Package)                                  |Tested on v1.13 |    Yes   |
| **Scipy** (Python Package)                                  |Tested on v1.0.0|    Yes   |
| **TreeTagger**                                              |Tested on v1.0.1|    Yes   |
| **SpeechRecognition** (Python Package)                      |Tested on v3.8.1|    Yes   |
| **PyAudio** (Python Package)                               |Tested on v0.2.11|    Yes   |
| **playsound** (Python Package)                              |    >= 1.2.2    |    Yes   |
| **editdistance** (Python Package)                           |     >= 0.4     |    Yes   |
| **pyobjc** (Python Package only for MacOS)                  |    >= 4.1      |    Yes   |
| [**portaudio**](http://www.portaudio.com)                  |Tested on v19.6.0|    Yes   |
| **pyttsx3** (Python Package)                                |     >= 2.7     |    Yes   |
| **SQLite**                                                  |      >= 3      |    Yes   |
| **OpenCV**                                                  |    >= 3.3.1    |    Yes   |
| [**Face Recognition**](https://github.com/ageitgey/face_recognition) (Python Package)|      >= 3      |    Yes   |
| QDarkStylesheet (Python Package)                            |    >= 2.3.1    | Optional |

QDarkStylesheet was used for a better looking GUI (highly recommended) and can be found in [this GitHub Repo](https://github.com/ColinDuquesnoy/QDarkStyleSheet)

# Developed by [Luca Angioloni](https://github.com/LucaAngioloni/) and [Francesco Pegoraro](https://github.com/SqrtPapere)

## License
Licensed under the term of [MIT License](http://en.wikipedia.org/wiki/MIT_License). See attached file LICENSE.
