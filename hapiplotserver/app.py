import os

from hapiclient import hapi
from hapiplotserver.plot import plot
from hapiplotserver.viviz import prepviviz

def app(conf):

    from flask import Flask, request, redirect, send_from_directory, url_for
    application = Flask(__name__)

    loglevel = conf['loglevel']
    cachedir = conf['cachedir']
    server_usecache = conf['usecache']
    appdir = os.path.abspath(os.path.dirname(__file__))

    @application.route("/html/favicon.ico")
    def favicon():
        if request.args.get('server') is None:
            return send_from_directory(appdir + "/html/", "favicon.ico")

    @application.route("/")
    def main():
        if request.args.get('server') is None:
            return send_from_directory(appdir + "/html/", "index.html")

        format = request.args.get('format')
        if format is None:
            format = 'png'

        if format == 'png':
            ct = {'Content-Type': 'image/png'}
        elif format == 'pdf':
            ct = {'Content-Type': 'application/pdf'}
        elif format == 'svg':
            ct = {'Content-Type': 'image/svg+xml'}
        else:
            ct = {'Content-Type': 'text/html'}

        server = request.args.get('server')
        if server is None:
            return 'A server argument is required, e.g., /?server=...', 400, {'Content-Type': 'text/html'}

        dataset = request.args.get('id')
        if dataset is None:
            return 'A dataset argument is required, e.g., /?server=...&id=...', 400, {'Content-Type': 'text/html'}

        parameters = request.args.get('parameters')
        if parameters is None and format != 'gallery':
            return 'A parameters argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

        start = request.args.get('time.min')
        if start is None and format != 'gallery':
            return 'A time.min argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

        stop = request.args.get('time.max')
        if start is None and format != 'gallery':
            return 'A time.max argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

        meta = None
        if start is None:
            try:
                meta = hapi(server, dataset)
                start = meta['startDate']
            except Exception as e:
                return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}

        if stop is None:
            if meta is None:
                try:
                    meta = hapi(server, dataset)
                except Exception as e:
                    return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}
            stop = meta['stopDate']

        usecache = request.args.get('usecache')
        if usecache is None:
            usecache = True
        elif usecache.lower() == "true":
            usecache = True
        elif usecache.lower() == "false":
            usecache = False
        else:
            return 'usecache must be true or false', 400, {'Content-Type': 'text/html'}

        if server_usecache is False and usecache is True:
            usecache = False
            if loglevel == 'debug':
                print('Application configuration has usecache=False so request to use cache is ignored.')

        transparent = request.args.get('transparent')
        if transparent is None:
            transparent = True
        elif transparent.lower() == "true":
            transparent = True
        elif transparent.lower() == "false":
            transparent = False
        else:
            return 'transparent must be true or false', 400, {'Content-Type': 'text/html'}

        dpi = request.args.get('dpi')
        if dpi is None:
            dpi = 300
        else:
            dpi = int(dpi)
            if dpi > 1200 or dpi < 1:
                return 'dpi must be <= 1200 and > 1', 400, {'Content-Type': 'text/html'}

        figsize = request.args.get('figsize')
        if figsize is None:
            figsize = (7, 3)
        else:
            figsizearr = figsize.split(',')
            figsize = (float(figsizearr[0]), float(figsizearr[1]))
            # TODO: Set limits on figsize?

        id = ""
        if parameters is not None:
            id = "&id=" + parameters.split(",")[0]
        else:
            meta = hapi(server, dataset)
            # Set first parameter shown to be first in dataset (if this is
            # not done the time variable is the first parameter shown, which
            # is generally not wanted.)
            id = "&id=" + meta['parameters'][1]['name']

        if format == 'gallery':
            prepviviz(server, dataset, **conf)
            url = url_for("viviz", _external=True)
            return redirect(url+"#catalog="+server + id, code=302)

        # Plot options
        opts = {'cachedir': cachedir, 'usecache': usecache, 'loglevel': loglevel, 'format': format, 'figsize': figsize, 'dpi': dpi, 'transparent': transparent}

        img = plot(server, dataset, parameters, start, stop,  **opts)

        ct['Content-Length'] = len(img[0])

        if img[1] is not None:
            ct["X-Error"] = img[1]

        return img[0], 200, ct

    # ../? in fuldir and thumbdir in viviz.py
    # return = url + "#catalog=..." and url = url_for("viviz", _external=True)
    # in format == 'gallery'

    # Serve index.htm for /viviz/ request
    @application.route("/viviz/")
    def viviz():
        return send_from_directory(cachedir+"/viviz", "index.htm")

    # Serve static files
    @application.route("/viviz/"+"<path:filename>")
    def vivizf(filename):
        print(filename)
        if filename == 'index.js' or '.json' in filename:
            # Force these files to not be cached by browser.
            print("Setting cache_timeout = 0 for " + filename)
            return send_from_directory(cachedir+"/viviz", filename, cache_timeout=0)
        else:
            return send_from_directory(cachedir+"/viviz", filename)

    return application
