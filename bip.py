from playsound import playsound
import sys, os

pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname).replace(" ", "%20")

print(fullpath)

playsound(fullpath + "/Resources/bip.wav")
