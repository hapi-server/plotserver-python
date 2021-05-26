def config(**kwargs):

    import os
    import logging
    import tempfile

    # TODO: Test validity of options
    # Test port: https://stackoverflow.com/a/43271125/1491619
    # Test if can write to cachedir
    # options.use = 0 or 1
    # options.loglevel = error, default, debug
    # options.threaded = 0 or 1
    # options.works = ... not more than # of cpus?

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
            "timeout": 90,
            "figsize": (7, 3),
            "format": 'png',
            "dpi": 144,
            "transparent": False}

    for key in conf:
        if key in kwargs:
            conf[key] = kwargs[key]

    if not os.path.exists(conf['cachedir']):
        os.makedirs(conf['cachedir'])

    # TODO: Add log-to-file option.
    # https://gist.github.com/ivanlmj/dbf29670761cbaed4c5c787d9c9c006b
    if conf['loglevel'] == 'error':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    return conf
