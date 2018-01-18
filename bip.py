from playsound import playsound
import sys, os

<<<<<<< HEAD
pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname).replace(" ", "%20")

print(fullpath)

playsound(fullpath + "/Resources/bip.wav")
=======


playsound("Resources/bip.wav")
>>>>>>> 5af8ef8ff86f5172a5ebe8cf2b279fd40d892261
