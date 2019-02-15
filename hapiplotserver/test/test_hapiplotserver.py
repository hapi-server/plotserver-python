import sys
import time
import urllib
import webbrowser
from hapiclient.util import urlopen 
#from PIL import Image

from hapiplotserver.main import hapiplotserver

if True:
    from multiprocessing import Process

    print("test_hapiplotserver.py: Starting server.")

    kwargs = {'port': 5002, 'workers': 4}
    process = Process(target=hapiplotserver, kwargs=kwargs)
    process.start()
    print("test_hapiplotserver.py: Sleeping for 1 second while server starts.")
    time.sleep(1)

    url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&format=gallery'
    print(' * Opening in browser tab:')
    print(' * ' + url)
    webbrowser.open(url, new=2)
    if sys.version_info[0] > 2:
        input("Press Enter to continue.")
    else:
        raw_input("Press Enter to continue.")

    try:
        if True:

            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&parameters=Time&time.min=1970-01-01Z&time.max=1970-01-02T00:00:00Z&format=png&usecache=False'
            print("test_hapiplotserver.py: Making request")
            img = urlopen(url)
            process.terminate()
            if len(img.read()) > 80000:
                print("test_hapiplotserver.py: \033[0;32mPASS\033[0m")
                sys.exit(0)
            else:
                print("test_hapiplotserver.py: \033[0;31mFAIL\033[0m")
                sys.exit(1)
            #Image.open(urllib.request.urlopen(url)).show()
        
        if False:
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&parameters=scalar&time.min=1970-01-01Z&time.max=1970-01-01T00:00:11Z&format=png&usecache=False'
            Image.open(urllib.request.urlopen(url)).show()

        if False:            
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=https://cdaweb.gsfc.nasa.gov/hapi&id=AC_H0_MFI&parameters=Magnitude&time.min=2001-01-01T05:00:00&time.max=2001-01-01T06:00:00&format=png&usecache=False'
            Image.open(urllib.request.urlopen(url)).show()
    
        if False:
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&format=gallery'
            print(' * Opening in browser tab:')
            print(' * ' + url)
    
        if False:
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&parameters=scalar&usecache=false&format=gallery'
            print(' * Opening in browser tab:')
            print(' * ' + url)
    
    except Exception as e:
        print(e)
        print("Terminating server.")
        process.terminate()
    
    input("Press Enter to terminate server.")
    print("Terminating server ...")
    process.terminate()
    print("Server terminated.")

if False:
    # Run in separate thread.
    # Note that it is not easy to terminate a thread, so multiprocessing
    # is used in gallery().
    from threading import Thread
    kwargs = {'port': 5002, 'loglevel': 'default'}
    thread = Thread(target=hapiplotserver, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()

if False:
    # Run in main thread
    kwargs = {'port': 5002, 'loglevel': 'default'}
    hapiplotserver(**kwargs)
    # Then open http://127.0.0.1:5001/

