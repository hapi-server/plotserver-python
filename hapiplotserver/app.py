import re
import os
import traceback
import urllib

from hapiclient import hapi
from hapiplotserver.log import log
from hapiplotserver.plot import plot
from hapiplotserver.viviz import vivizconfig

import platform
python_version = platform.python_version()
from hapiclient import __version__ as hapiclient_version
from hapiplot import __version__ as hapiplot_version
from hapiplotserver import __version__ as hapiplotserver_version


def app(conf):

    from flask import Flask, Response, request, redirect, send_from_directory, make_response, url_for
    from werkzeug.routing import BaseConverter
    application = Flask(__name__)

    loglevel = conf['loglevel']
    cachedir = conf['cachedir']
    appdir = os.path.abspath(os.path.dirname(__file__))

    with open(appdir + "/html/" + "index.html", "rt") as f:
        indexhtml = f.read()
        indexhtml = indexhtml.replace("<code>hapiplotserver-VERSION</code>", "<code>hapiplotserver-" + hapiplotserver_version + "</code>")
        indexhtml = indexhtml.replace("<code>hapiplot-VERSION</code>", "<code>hapiplot-" + hapiplot_version + "</code>")
        indexhtml = indexhtml.replace("<code>hapiclient-VERSION</code>", "<code>hapiclient-" + hapiclient_version + "</code>")
        indexhtml = indexhtml.replace("<code>python-VERSION</code>", "<code>python-" + python_version + "</code>")

    def cacheopts(cachestr):
        usecache = request.args.get(cachestr)
        if usecache is None:
            usecache = True
        elif usecache.lower() == "true":
            usecache = True
        elif usecache.lower() == "false":
            usecache = False
        else:
            return cachestr + ' must be true or false', 400, {'Content-Type': 'text/html'}

        if conf[cachestr] is False and usecache is True:
            usecache = False
            if loglevel == 'debug':
                log('app(): Application configuration has ' + cachestr + '=False so request to use cache is ignored.')

        return usecache

    @application.route("/favicon.ico")
    def favicon():
        if request.args.get('server') is None:
            return send_from_directory(appdir + "/html/", "favicon.ico")

    @application.route("/")
    def main():

        server = request.args.get('server')
        if server is None:
            return indexhtml, 200, {'Content-Type': 'text/html'}
            #return send_from_directory(appdir + "/html/", "index.html")
        else:
            server = urllib.parse.unquote(server, encoding='utf-8')

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

        #if loglevel == 'debug':
        #    print(request.args)

        dataset_str = 'id'
        dataset = None
        if request.args.get('id') is not None:
            dataset = request.args.get('id')
        if request.args.get('dataset') is not None:
            dataset = request.args.get('dataset')
            dataset_str = 'dataset'
        if dataset is None and format != 'gallery':
            return 'A dataset id argument is required, e.g., /?server=...&'+dataset_str+'=...', 400, {'Content-Type': 'text/html'}
        else:
            dataset = urllib.parse.unquote(dataset, encoding='utf-8')

        parameters = request.args.get('parameters')
        if parameters is None and format != 'gallery':
            return 'A parameters argument is required if format != "gallery", e.g., /?server=...&'+dataset_str+'=...&amp;parameters=...', 400, {'Content-Type': 'text/html'}
        else:
            if parameters is not None:
                parameters = urllib.parse.unquote(parameters, encoding='utf-8')

        start = None
        if request.args.get('time.min') is not None:
            start = request.args.get('time.min')
        if request.args.get('start') is not None:
            start = request.args.get('start')
        if start is None and format != 'gallery':
            return 'A time.min or start argument is required if format != "gallery", e.g., /?server=...&'+dataset_str+'id=...&amp;parameters=...&amp;start=...&amp;stop=...', 400, {'Content-Type': 'text/html'}
        else:
            if start is not None:
                start = urllib.parse.unquote(start)

        stop = None
        if request.args.get('time.max') is not None:
            stop = request.args.get('time.max')
        if request.args.get('stop') is not None:
            stop = request.args.get('stop')
        if stop is None and format != 'gallery':
            return 'A time.max argument is required if format != "gallery", e.g., /?server=...&id=...&amp;parameters=...', 400, {'Content-Type': 'text/html'}
        else:
            if stop is not None:
                stop = urllib.parse.unquote(stop)

        meta = None
        if start is None and format != 'gallery':
            try:
                meta = hapi(server, dataset)
                start = meta['startDate']
            except Exception as e:
                return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}

        if stop is None and format != 'gallery':
            if meta is None:
                try:
                    meta = hapi(server, dataset)
                except Exception as e:
                    return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}
            stop = meta['stopDate']

        usecache = cacheopts('usecache')
        usedatacache = cacheopts('usedatacache')

        if usedatacache is False:
            usecache = False

        transparent = request.args.get('transparent')
        if transparent is None:
            transparent = conf['transparent']
        elif transparent.lower() == "true":
            transparent = True
        elif transparent.lower() == "false":
            transparent = False
        else:
            return 'transparent must be true or false', 400, {'Content-Type': 'text/html'}

        dpi = request.args.get('dpi')
        if dpi is None:
            dpi = conf['dpi']
        else:
            dpi = int(dpi)
            if dpi > 1200 or dpi < 1:
                return 'dpi must be <= 1200 and > 1', 400, {'Content-Type': 'text/html'}

        figsize = request.args.get('figsize')
        if figsize is None:
            figsize = conf['figsize']
        else:
            figsize = urllib.parse.unquote(figsize)
            figsizearr = figsize.split(',')
            figsize = (float(figsizearr[0]), float(figsizearr[1]))
            # TODO: Set limits on figsize?

        if format == 'gallery':
            if dataset is None:
                """
                If many datasets, vivizconfig() call will take a long
                time and there will be no feedback.
                """
                #return 'An id argument is required if format = "gallery", e.g., /?server=...&id=...[&amp;parameters=...]',\
                #       400, {'Content-Type': 'text/html'}
                pass

            # https://stackoverflow.com/questions/30006740/how-can-i-tell-flask-not-to-add-host-scheme-info-to-my-redirect
            # If used behind a proxy, we need relative redirects.
            class FixedLocationResponse(Response):
                autocorrect_location_header = False

            try:
                indexhtm, vivizhash = vivizconfig(server, dataset, parameters, start, stop, **conf)

                red = "viviz/" + indexhtm + "#" + vivizhash
                mode = request.args.get('mode')
                if mode:
                    red = red + "&mode=" + mode
                log("hapiplotserver.app.main(): Redirecting to " + red)
                #return redirect(red, code=302)
                return redirect(red, code=302, Response=FixedLocationResponse)
            except Exception as e:
                log(traceback.format_exc())
                message = traceback.format_exc().split('\n')
                return message, 500, {'Content-Type': 'text/html'}

        # Plot function options
        opts = {'cachedir': cachedir, 'usecache': usecache, 'usedatacache': usedatacache, 'loglevel': loglevel, 'format': format, 'figsize': figsize, 'dpi': dpi, 'transparent': transparent}

        img = plot(server, dataset, parameters, start, stop,  **opts)

        ct['Content-Length'] = len(img[0])

        if img[1] is not None:
            ct["X-HAPI-Error"] = img[1]

        return img[0], 200, ct

    # Serve index.htm for /viviz/ request
    @application.route("/viviz/")
    def viviz():
        pass

    # https://stackoverflow.com/a/5872904
    class RegexConverter(BaseConverter):
        def __init__(self, url_map, *items):
            super(RegexConverter, self).__init__(url_map)
            self.regex = items[0]

    application.url_map.converters['regex'] = RegexConverter

    if True:
        @application.route('/viviz/catalogs/<path:filename>')
        def vivizid2(filename):
            print("\n0000000 " + filename)

            response = make_response(send_from_directory(cachedir + "/viviz-hapi/catalogs", filename))
            #response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = 'inline'
            return response

    @application.route('/viviz/<regex("[0-9a-f]{4}"):uid>')
    def vivizid(uid):
        print("\n-------" + uid)
        #fpath = os.path.join(cachedir, "viviz-galleries", uid, filename)
        response = make_response(send_from_directory(cachedir + "/viviz-hapi", uid))
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = 'inline'
        return response

    if True:
        # Serve static files
        @application.route("/viviz/hapi/" + "<path:filename>")
        def vivizidfiles(filename):
            print("\n+++++++" + filename)
            response = make_response(send_from_directory(cachedir + "/viviz-hapi", filename))
            return response

    # Serve static files
    @application.route("/viviz/" + "<path:filename>")
    def vivizf(filename):
        fname, fext = os.path.splitext(cachedir + "/viviz/" + filename)
        response = make_response(send_from_directory(cachedir + "/viviz", filename))
        if not fext:
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = 'inline'
        return response

    from werkzeug.exceptions import InternalServerError
    @application.errorhandler(InternalServerError)
    def internal_error(error):
        print(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        for i in range(0, len(message)):
            message[i] = re.sub(r'(.*)File ".*/(.*)"', r'\1File \2', message[i])
            message[i] = re.sub(r'\s', r'&nbsp;', message[i])
        msg = "<br/>".join(message)
        # TODO: Duplicate code in plot.py
        vers = "| hapiplotserver v" + hapiplotserver_version + " | "
        vers = vers + "hapiplot v" + hapiplot_version + " | "
        vers = vers + "hapiclient v" + hapiclient_version + " | "
        vers = vers + "matplotlib v" + matplotlib_version + " | "
        vers = vers + "python v" + python_version + " | <br/>"
        return vers + msg, 500
 
    return application
