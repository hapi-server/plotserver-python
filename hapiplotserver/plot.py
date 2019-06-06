from hapiclient.hapi import hapi, request2path
from hapiclient.hapiplot import hapiplot

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
        data, meta = hapi(server, dataset, parameters, start, stop, **opts)
        if kwargs['loglevel'] == 'debug': print('hapiplotserver.plot(): Time for hapi() call = %f' % (time.time()-tic))
    except Exception as e:
        print(traceback.format_exc())
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

        meta = hapiplot(data, meta, **popts)
        pn = -1 + len(meta['parameters'])
        img = meta['parameters'][pn]['hapiplot']['image']

        if kwargs['loglevel'] == 'debug':
            print('hapiplotserver.plot(): Time for hapiplot() call = %f' % (time.time()-tic))
        if not img:
            message = "hapiplot.py cannot plot parameter " + parameters
            return errorimage(kwargs['figsize'], kwargs['format'], kwargs['dpi'], message)
        else:
            return img, None
    except Exception as e:
        print(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        return errorimage(kwargs['figsize'], kwargs['format'], kwargs['dpi'], message)
