import os
import io
import sys
import time
import webbrowser
import requests
from PIL import Image

from hapiplotserver import hapiplotserver

PORT = 5003

print("test_hapiplotserver.py: Starting server.")

if False:
    # Run in main thread
    kwargs = {'port': PORT, 'loglevel': 'default'}
    hapiplotserver(**kwargs)
    # Then open http://127.0.0.1:PORT/
    sys.exit(0)

if True:

    kwargs = {'port': PORT, 'workers': 1, 'loglevel': 'debug'}
    import multiprocessing as mp
    #import platform
    #if platform.system() == "Darwin": print(mp.get_context("spawn"))
    process = mp.Process(target=hapiplotserver, kwargs=kwargs)
    process.start()
    print("test_hapiplotserver.py: Sleeping for 3 seconds while server starts.")
    time.sleep(3)

try:

    if False:
        url = 'http://127.0.0.1:' + str(kwargs['port']) + '/?server=http://hapi-server.org/servers/TestData2.0/hapi&id=dataset1&parameters=scalar&time.min=1970-01-01Z&time.max=1970-01-01T00:00:11Z&transparent=false&usecache=False'
        r = requests.get(url)
        r.raise_for_status()
        with io.BytesIO(r.content) as fi:
            img = Image.open(fi)
        if 'hapiclient.hapiplot.error' in img.info:
            print("test_hapiplotserver.py: \033[0;31mFAIL\033[0m")
        else:
            print("test_hapiplotserver.py: \033[0;32mPASS\033[0m")

    if True:
        url = 'http://127.0.0.1:' + str(kwargs['port']) \
                + '/?server=http://hapi-server.org/servers/TestData2.0/hapi&id=dataset1&parameters=scalar' \
                + '&format=gallery'
        print(' * Opening in browser tab:')
        print(' * ' + url)
        webbrowser.open(url, new=2)

except Exception as e:
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    NC='\033[0m'
    print(RED + "FAIL" + NC)

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

