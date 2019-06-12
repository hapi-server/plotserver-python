import os
import io
import sys
import time
import webbrowser
import requests
from PIL import Image
from multiprocessing import Process
from hapiplotserver.main import hapiplotserver

PORT = 5003

print("test_hapiplotserver.py: Starting server.")

kwargs = {'port': PORT, 'workers': 4, 'loglevel': 'debug'}
process = Process(target=hapiplotserver, kwargs=kwargs)
process.start()
print("test_hapiplotserver.py: Sleeping for 3 seconds while server starts.")
time.sleep(3)

try:

    if True:
        url = 'http://127.0.0.1:' + str(kwargs['port']) + '/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&parameters=Time&time.min=1970-01-01Z&time.max=1970-01-02T00:00:00Z&format=png&usecache=False'
        r = requests.get(url)
        r.raise_for_status()
        with io.BytesIO(r.content) as fi:
            img = Image.open(fi)
        if 'hapiclient.hapiplot.error' in img.info:
            print("test_hapiplotserver.py: \033[0;31mFAIL\033[0m")
        else:
            print("test_hapiplotserver.py: \033[0;32mPASS\033[0m")

    if True:
        url = 'http://127.0.0.1:' + str(kwargs['port']) + '/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&format=gallery'
        print(' * Opening in browser tab:')
        print(' * ' + url)
        webbrowser.open(url, new=2)

except Exception as e:
    print(e)
    print("Terminating server.")
    process.terminate()

# Keep server running for visual test of gallery in web page.
input("\nPress Enter to terminate server.\n")
print("Terminating server ...")
process.terminate()
print("Server terminated.")

if False:
    # Run in separate thread.
    # Note that it is not easy to terminate a thread, so multiprocessing
    # is used in gallery().
    from threading import Thread
    kwargs = {'port': PORT, 'loglevel': 'default'}
    thread = Thread(target=hapiplotserver, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()

if False:
    # Run in main thread
    kwargs = {'port': 5002, 'loglevel': 'default'}
    hapiplotserver(**kwargs)
    # Then open http://127.0.0.1:PORT/

