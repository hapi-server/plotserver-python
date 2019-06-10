def config(**kwargs):

    import os
    import logging
    import tempfile

    # If `workers` > 0, use Gunicorn with this many workers;
    # `threaded` is ignored.
    workers = 0

    loglevel = 'default'
    # error: show only errors
    # default: show requests and errors
    # debug: show requests, errors, and debug messages

    conf = {"port": 5000,
            "cachedir": os.path.join(tempfile.gettempdir(), 'hapi-data'),
            "usecache": True,
            "usedatacache": True,
            "loglevel": loglevel,
            "threaded": True,
            "workers": workers,
            "figsize": (7, 3),
            "format": 'png',
            "dpi": '144',
            "transparent": False}

    for key in conf:
        if key in kwargs:
            conf[key] = kwargs[key]

    # TODO: Add log-to-file option.
    # https://gist.github.com/ivanlmj/dbf29670761cbaed4c5c787d9c9c006b
    if conf['loglevel'] == 'error':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    return conf

