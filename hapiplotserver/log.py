import os
import datetime

def log(msg):
    print(str(datetime.datetime.utcnow()) + "Z [" + str(os.getpid()) + "] " + msg)
