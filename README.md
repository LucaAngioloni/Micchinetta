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
The scenario of this tests will be a well known and restricted context, in fact MICChinetta will be used by people attending the MICC laboratory, however the utility of the application transcends from this and the results obtained will be valid also in other similar scenarios.

### Environment and tasks
We placed our system right by the vending machine at MICC, providing it an internet connection (not really reliable that
particular day due to work in progress) and installing all necessary software. We gathered all available staff, in couples or alone, and we read them a list of tasks, briefly explaining the application whenever someone had no idea about the purpose.

Tasks available for the users to read con- sisted of:
- To be recognized: Present your self in front of the machine and let it recognize you
- Wrong recognition: Simulate a wrong recognition and say it to the system.
- Ask for a product: You are hungry or thirsty, so you ask for a product.
- Ask for more products: You are very hungry or thirsty, so you ask for more than one product.
- Remove a product: You changed your mind, remove a product.
- Remove more producsts: You changed your mind, remove some products.
- Confirm the purchase: You are finished, agree to the transaction.

After the completion, we asked the users to compile a google form structured as a SEQ (Single Ease Question) with a 7-point
rating scale:
1. I found the reply time too high.
2. I prefer using the mobile application instead of this system.
3. It is hard to use it.
4. The facial recognition works correctly.
5. The Graphic interface is pleasant.
6. I can trust the system.
7. MICChinetta can understand my request.
8. MICChinetta’s replys are wrong.

Moreover we provided the users the chance to express some optional comments for each question.

### Results
*Error trials*: We gathered 13 users, each tried 7 task, so the total amount of trials is 91. Just 12 of these tasks failed, but only 2 resulted in a critical failure due to the lack of connection to internet, the other 4 where due to fails in speech-recognition and where recovered only by repeating the request.

Figure 10 shows that users’ opinions vary when asked if the latency between MICChinetta’s replies are too high. This may be linked to the fact that reply time varies with respect to internet connection. Moreover some user aknowledge the compu- tational efficiency required for speech recog- nition and pos-tagging and replies are bi- ased.

Figure 11 shows that the majority of the users would prefer to use the VUI instead of the mobile phone app.

Figure 12 shows that most of the users found the system to be self explanatory, this is indeed crucial using a never-seen application. Moreover users agree about the pleasentness of the Graphical Interface demonstrated in Figure 13.

Figure 14 affirms that face recognition was definitely working, this is a factor in the trust placed by the user, reported in Figure 15, and confirmed in the next figures.

Figure 16 and Figure 17 are a good demonstration of the conversation skills of the system, it can understand what users ask and answers correctly. This is maybe the best result we had hoped for in devel- oping MICChinetta.

## Conclusion
We have presented MICChinetta, a VUI-GUI system to provide assistance in the process of purchasing snacks at a vending machine. We demonstrated the useful functionality of been able to recognize known people using face recognition and the effectiveness of vocal interactions with an automated system. Systems like this are growing fast in popularity for the most varyious scenarios, like car driving, mobile phones and very more. We discovered the possibilities of such methods for augmenting human-computer-interactions using a prototype like MICChinetta, showing pros and cons, like the latency in the responses, but considering it as a study this is indeed improvable from many aspects. We could have used better machines for carrying out all the computation in local, like speech-to-text, without relying over internet connection. Our final study confirmed that MICChinetta, but more in general VUIs, can do almost everything a GUI can do, not reducing task time, but giving the users different possibilities and experiences without using arms or hands. We believe that pushing our self in this direction and improving this techonologies, automated system will efficiently substitute standard interfaces where less and less interaction and effort from humans is required.

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
