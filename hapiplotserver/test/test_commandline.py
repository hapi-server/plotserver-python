import io
import os
import sys
import time
import requests
from PIL import Image

PORT = 5003

urlfile = os.path.dirname(os.path.realpath(__file__)) + "/urls.txt"

print("test_commandline.py: Killing any running hapiplotserver listening on port " + str(PORT))
os.system("pkill -f 'hapiplotserver --port " + str(PORT) + "'")

cmd = "hapiplotserver --port " + str(PORT) + " --workers 2 --loglevel debug &"
print("test_commandline.py: Starting server using " + cmd)
os.system(cmd)

print("test_commandline.py: Sleeping for 2 seconds before running tests.")
time.sleep(2)

exit_signal = 0
urlfile = os.path.dirname(os.path.realpath(__file__)) + "/urls.txt"
urlo = "http://localhost:" + str(PORT) + "/"
with open(urlfile) as f:
    for url in f:
        print("test_commandline.py: Testing " + urlo + url)
        r = requests.get(urlo + url)
        r.raise_for_status()
        with io.BytesIO(r.content) as fi:
            img = Image.open(fi)
            if 'hapiclient.hapiplot.error' in img.info:
                print("test_commandline.py: \033[0;31mFAIL\033[0m")
                exit_signal = 1
                img.show()
            else:
                print("test_commandline.py: \033[0;32mPASS\033[0m")

print("test_commandline.py: Killing any running hapiplotserver listening on port " + str(PORT))
os.system("pkill -f 'hapiplotserver --port " + str(PORT) + "'")
sys.exit(exit_signal)
