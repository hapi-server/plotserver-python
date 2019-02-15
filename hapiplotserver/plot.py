from hapiclient.hapi import hapi
from hapiclient.util import system, download
from hapiclient.hapiplot import hapiplot, imagepath

def errorimage(figsize, format, dpi, message):

    import re
    from io import BytesIO
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    j = 0
    msg = message
    for i in range(0,len(message)):
        if message[i].startswith("  File"):
            j = i
    if j > 0:
        msg = re.sub(r'.*\/.*\/(.*)', r'\1', message[j]).strip()
        msg = msg.replace('"', '').replace(',', '')
        msg = msg + ":"
        for k in range(j+1, len(message)):
            if message[k].strip() != '':
                msg = msg + "\n" + message[k].strip()

    fig = Figure(figsize=figsize)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.plot([0, 0], [0, 0])
    ax.set(ylim=(-1, 1), xlim=(-1, 1))
    ax.set_axis_off()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    ax.text(-1, 1, msg, verticalalignment='top', horizontalalignment='left')

    figdataObj = BytesIO()
    canvas.print_figure(figdataObj, format=format, facecolor='red', bbox_inches='tight', dpi=dpi)
    figdata = figdataObj.getvalue()

    return figdata

def plot(server, dataset, parameters, start, stop, **kwargs):

    import os
    import traceback
    import time

    cachedir = kwargs['cachedir'] if 'cachedir' in kwargs else CACHEDIR
    usecache = kwargs['usecache'] if 'usecache' in kwargs else USECACHE
    loglevel = kwargs['loglevel'] if 'loglevel' in kwargs else LOGLEVEL
    figsize = kwargs['figsize'] if 'figsize' in kwargs else (7, 3)
    format = kwargs['format'] if 'format' in kwargs else 'png'
    dpi = kwargs['dpi'] if 'dpi' in kwargs else 144
    transparent = kwargs['transparent'] if 'transparent' in kwargs else False

    logging = False
    if loglevel == 'debug': logging = True

    if usecache:
        opts = {'cachedir': cachedir, 'format': format, 'figsize': figsize, 'dpi': dpi, 'transparent': transparent}
        fnameimg = imagepath(server, dataset, parameters, start, stop, **opts)
        if os.path.isfile(fnameimg):
            if loglevel == 'debug': print('hapiplotserver.plot(): Returning cached image from ' + fnameimg)
            with open(fnameimg, "rb") as f:
                return f.read(), None
    
    try:
        tic = time.time()
        opts = {'logging': logging, 'cachedir': cachedir, 'usecache': usecache}
        data, meta = hapi(server, dataset, parameters, start, stop, **opts)
        if loglevel == 'debug': print('hapiplotserver.plot(): Time for hapi() call = %f' % (time.time()-tic))
    except Exception as e:
        print(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        return errorimage(figsize, format, dpi, message), message

    try:
        tic = time.time()
        popts = {'logging': logging, 'cachedir': cachedir, 'returnimage': True, 'transparent': transparent, 'usecache': usecache, 'returnformat': format, 'figsize': figsize, 'dpi': dpi}
        img = hapiplot(data, meta, **popts)
        if loglevel == 'debug': print('hapiplotserver.plot(): Time for hapiplot() call = %f' % (time.time()-tic))
        if not img:
            message = "hapiplot.py cannot plot parameter " + parameters
            return errorimage(figsize, format, dpi, message), message
        else:
            return img, None
    except Exception as e:
        print(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        return errorimage(figsize, format, dpi, message), message
