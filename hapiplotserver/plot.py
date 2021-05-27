from hapiclient.hapi import hapi, request2path
from hapiplot import hapiplot
from hapiplotserver.log import log
from hapiclient import __version__ as hapiclient_version


def errorimage(figsize, format, dpi, message):
    """Return a red png with hapiclient error message"""

    import re
    from io import BytesIO
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    j = 0
    # Look for last line in stack trace with HAPI error message.
    for i in range(0, len(message)):
        if message[i].startswith("hapiclient.util.error.<locals>.HAPIError:"):
            j = i
    if j > 0:
        msg = message[j].replace('hapiclient.util.error.<locals>.HAPIError:', '')
    else:
        for i in range(0, len(message)):
            message[i] = re.sub(r'(.*)File ".*/(.*)"', r'\1File \2', message[i])
        msg = "\n".join(message)

    msg = "hapiclient version " + hapiclient_version + "\n" + msg

    msgo = msg
    # Make URL easier to read on image by inserting newlines.
    msg = re.sub(r' http(.*)', r'\nhttp\1', msg)
    msg = msg.replace("&", "\n   &")
    msg = msg.replace("?", "\n   &")

    fig = Figure(figsize=figsize)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.plot([0, 0], [0, 0])
    ax.set(ylim=(-1, 1), xlim=(-1, 1))
    ax.set_axis_off()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    ax.text(-1, 1, msg, verticalalignment='top', horizontalalignment='left')

    figdata_obj = BytesIO()
    canvas.print_figure(figdata_obj, format=format, facecolor='red', bbox_inches='tight', dpi=dpi)

    if msg == '' or format != 'png':
        # No error or format is not for png
        # Adding metadata to non-png files not tested or not implemented.
        # TODO: Implement adding metadata to JPG, PDF, and SVG.
        figdata = figdata_obj.getvalue()
    else:
        # Add error message to metadata
        figdata = add_metadata(figdata_obj, msgo)

    # Remove newlines with ";" in msg as it will be in a HTTP header.
    return figdata, msgo.replace('\n', ';')


def add_metadata(figdata_obj, msg):

    from io import BytesIO
    from PIL import Image, PngImagePlugin

    meta = PngImagePlugin.PngInfo()
    meta.add_text('hapiclient.hapiplot.error', msg, 0)

    # Add metadata from Matplotlib
    im = Image.open(figdata_obj)

    for k, v in im.info.items():
        meta.add_text(str(k), str(v), zip=0)

    figdata_obj2 = BytesIO()
    im = Image.open(figdata_obj)
    im.save(figdata_obj2, "PNG", pnginfo=meta)

    return figdata_obj2.getvalue()


def plot(server, dataset, parameters, start, stop, **kwargs):

    import traceback
    import time

    logging = False
    if kwargs['loglevel'] == 'debug': logging = True

    try:
        tic = time.time()
        opts = {'logging': logging,
                'cachedir': kwargs['cachedir'],
                'usecache':  kwargs['usedatacache']
                }
        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.plot(): Calling hapi() to get data')
        data, meta = hapi(server, dataset, parameters, start, stop, **opts)
        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.plot(): Time for hapi() call = %f' % (time.time()-tic))
    except Exception as e:
        log(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        return errorimage(kwargs['figsize'], kwargs['format'], kwargs['dpi'], message)

    try:
        tic = time.time()
        popts = {'logging': logging,
                 'cachedir': kwargs['cachedir'],
                 'returnimage': True,
                 'useimagecache': kwargs['usecache'],
                 'saveimage': True,
                 'rcParams': {'savefig.transparent': kwargs['transparent'],
                              'savefig.format': kwargs['format'],
                              'savefig.dpi': kwargs['dpi'],
                              'figure.figsize': kwargs['figsize']
                              }
                 }

        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.plot(): Calling hapiplot()')

        meta = hapiplot(data, meta, **popts)
        pn = -1 + len(meta['parameters'])
        img = meta['parameters'][pn]['hapiplot']['image']

        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.plot(): Time for hapiplot() call = %f' % (time.time()-tic))
        if not img:
            message = "hapiplot.py cannot plot parameter " + parameters
            return errorimage(kwargs['figsize'], kwargs['format'], kwargs['dpi'], message)
        else:
            return img, None
    except Exception as e:
        log(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        return errorimage(kwargs['figsize'], kwargs['format'], kwargs['dpi'], message)
