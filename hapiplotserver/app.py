import re
import os
import traceback

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

        dataset = request.args.get('id')
        if dataset is None and format != 'gallery':
            return 'A dataset id argument is required, e.g., /?server=...&id=...', 400, {'Content-Type': 'text/html'}

        parameters = request.args.get('parameters')
        if parameters is None and format != 'gallery':
            return 'A parameters argument is required if format != "gallery", e.g., /?server=...&id=...&amp;parameters=...', 400, {'Content-Type': 'text/html'}

        start = request.args.get('time.min')
        if start is None and format != 'gallery':
            return 'A time.min argument is required if format != "gallery", e.g., /?server=...&id=...&amp;parameters=...', 400, {'Content-Type': 'text/html'}

        stop = request.args.get('time.max')
        if start is None and format != 'gallery':
            return 'A time.max argument is required if format != "gallery", e.g., /?server=...&id=...&amp;parameters=...', 400, {'Content-Type': 'text/html'}

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


            try:
                indexhtm, vivizhash = vivizconfig(server, dataset, parameters, start, stop, **conf)
                # Get full URL
                url = url_for("viviz", _external=True)
                red = url + indexhtm + "#" + vivizhash
                log("hapiplotserver.app.main(): Redirecting to " + red)
                return redirect(red, code=302)
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

    @application.route('/viviz/<regex("[0-9a-f]{4}"):uid>')
    def vivizid(uid):
        response = make_response(send_from_directory(cachedir + "/viviz-hapi", uid))
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = 'inline'
        return response


    # Serve static files
    @application.route("/viviz/hapi/" + "<path:filename>")
    def vivizidfiles(filename):
        print(filename)
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
        #TODO
        #vers = "hapiplotserver v" + __version__
        vers = "hapiclient v" + hapiclient_version + "<br/>"
        return vers + msg, 500
 
    return application
