def config(**kwargs):

    import os
    import logging
    import tempfile

    # If > 0, use Gunicorn with this many workers. THREADED is ignored.
    WORKERS = 0

    LOGLEVEL = 'default'
    # error: show only errors
    # default: show requests and errors
    # debug: show requests, errors, and debug messages

    conf = {}
    conf['port'] = kwargs['port'] if 'port' in kwargs else 5000
    conf['cachedir'] = kwargs['cachedir'] if 'cachedir' in kwargs else os.path.join(tempfile.gettempdir(), 'hapi-data')
    conf['usecache'] = kwargs['usecache'] if 'usecache' in kwargs else True
    conf['usedatacache'] = kwargs['usedatacache'] if 'usedatacache' in kwargs else True
    conf['loglevel'] = kwargs['loglevel'] if 'loglevel' in kwargs else LOGLEVEL
    conf['threaded'] = kwargs['threaded'] if 'threaded' in kwargs else True
    conf['workers'] = kwargs['workers'] if 'workers' in kwargs else WORKERS
    conf['figsize'] = kwargs['figsize'] if 'figsize' in kwargs else (7, 3)
    conf['format'] = kwargs['format'] if 'format' in kwargs else 'png'
    conf['dpi'] = kwargs['dpi'] if 'dpi' in kwargs else 144
    conf['transparent'] = kwargs['transparent'] if 'transparent' in kwargs else False

    # TODO: Add log-to-file option.
    # https://gist.github.com/ivanlmj/dbf29670761cbaed4c5c787d9c9c006b
    if conf['loglevel'] == 'error':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    return conf

