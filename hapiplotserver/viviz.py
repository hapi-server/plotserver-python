from hapiplotserver.log import log


def getviviz(**kwargs):
    """Download ViViz web application"""

    import os
    import zipfile
    import requests

    reinstall = False
    if 'reinstall' in kwargs:
        reinstall = kwargs['reinstall']

    log('hapiplotserver.viviz(): reinstall = {}'.format(reinstall))

    vivizdir = kwargs['cachedir'] + "/viviz"

    if reinstall or not os.path.exists(vivizdir):
        if not os.path.exists(kwargs['cachedir']):
            log('hapiplotserver.viviz(): Creating {}'.format(kwargs['cachedir']))
            os.makedirs(kwargs['cachedir'])

        url = 'https://github.com/rweigel/viviz/archive/master.zip'

        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.viviz(): Downloading \n\t' + url + '\n\tto\n\t' + kwargs['cachedir'])

        file = kwargs['cachedir'] + '/viviz-master.zip'

        try:
            r = requests.get(url, allow_redirects=True)
        except requests.exceptions.RequestException as e:
            print(e)

        open(file, 'wb').write(r.content)

        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.viviz(): Unzipping ' + file)

        zipref = zipfile.ZipFile(file, 'r')
        zipref.extractall(kwargs['cachedir'])
        zipref.close()

        os.rename(vivizdir + "-master", vivizdir)

    else:
        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.viviz(): Found ViViz at ' + vivizdir)


def req2slug(server, dataset, parameters, start, stop):
    """Convert HAPI request parameters to sanitized string for part of file name"""

    from slugify import slugify

    # str() is used to convert None to 'None' if needed.
    slug = server + '-' + str(dataset) + '-' + str(parameters) + '-' + str(start) + '-' + str(stop)
    slug = slugify(slug, replacements=[['|', '_or_'], ['%', '_pct_']])

    return slug


def vivizconfig(server, dataset, parameters, start, stop, **kwargs):
    """Create ViViz configuration catalog and return ViViz URL hash"""

    import os
    import shutil
    import hashlib
    from hapiclient import hapi

    slug = req2slug(server, dataset, parameters, start, stop)

    gallery_dir = os.path.join(kwargs['cachedir'], "viviz-hapi")
    viviz_dir = os.path.join(kwargs['cachedir'], "viviz")

    if not os.path.exists(gallery_dir):
        log('hapiplotserver.vivizconfig(): Creating {}'.format(gallery_dir))
        os.makedirs(gallery_dir)

    indexjs   = os.path.join(gallery_dir, 'index-' + slug + '.js')
    indexhtm  = os.path.join(gallery_dir, 'index-' + slug + '.htm')
    indexjso  = os.path.join(viviz_dir, 'index.js')
    indexhtmo = os.path.join(viviz_dir, 'index.htm')

    try:
        shutil.copyfile(indexjso, indexjs)
    except:
        log("hapiplotserver.viviz.vivizconfig(): Getting ViViz (cache dir {} removed?)".format(kwargs['cachedir']))
        # Creates directory viviz in cachedir
        getviviz(**{**kwargs, **{"reinstall": True}})

    try:
        shutil.copyfile(indexjso, indexjs)
    except:
        print("Problem with ViViz installation.")

    if kwargs['loglevel'] == 'debug':
        log('hapiplotserver.viviz.vivizconfig(): Wrote %s' % indexjs)

    shutil.copyfile(indexhtmo, indexhtm)
    if kwargs['loglevel'] == 'debug':
        log('hapiplotserver.viviz.vivizconfig(): Wrote %s' % indexhtm)

    fid = hashlib.md5(bytes(slug, 'utf8')).hexdigest()
    indexhtm_hash = os.path.join(gallery_dir, fid[0:4])
    if os.path.isfile(indexhtm_hash):
        os.remove(indexhtm_hash)
        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.viviz.vivizconfig(): Removed existing %s' % indexhtm_hash)

    if kwargs['loglevel'] == 'debug':
        log('hapiplotserver.viviz.vivizconfig(): Symlinking %s with %s' % (indexhtm, indexhtm_hash))
    os.symlink(indexhtm, indexhtm_hash)
    indexhtm_hash = fid[0:4]

    indexjs_rel = 'hapi/index-' + slug + '.js'
    with open(indexhtm) as f:
        tmp = f.read().replace('<script type="text/javascript" src="index.js',
                               '<script type="text/javascript" src="' + indexjs_rel)
    with open(indexhtm, "w") as f:
        f.write(tmp)

    if dataset is None:
        import requests
        # See if server provides all.json
        xurl = server + "/all.json"
        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.viviz.vivizconfig(): Getting %s' % xurl)

        try:
            r = requests.get(xurl, allow_redirects=True)
        except Exception as e:
            r = False

        if r and r.status_code == 200:
            if kwargs['loglevel'] == 'debug':
                log('hapiplotserver.viviz.vivizconfig(): Got %s' % xurl)
            catalog = r.json()
            dataset0 = list(catalog.keys())[0]
            adddatasets(server, catalog, indexjs, **kwargs)
        else:
            log('hapiplotserver.viviz.vivizconfig(): Could not get %s' % xurl)
            catalog = hapi(server)
            dataset0 = catalog["catalog"][0]["id"]  # First dataset
            for i in range(len(catalog["catalog"])):
                dataset = catalog["catalog"][i]["id"]
                adddataset(server, dataset, indexjs, **kwargs)
    else:
        dataset0 = dataset
        adddataset(server, dataset, indexjs, **kwargs)

    gid = ""
    # ID is ViViz gallery ID. In ViViz, the server URL is the catalog ID.
    if parameters is not None:
        # TODO: Check that all given parameters are valid
        gid = "&id=" + parameters.split(",")[0]
    else:
        meta = hapi(server, dataset0)
        # Set first parameter shown to be first in dataset (if this is
        # not done the time variable is the first parameter shown, which
        # is generally not wanted.)
        gid = "&id=" + meta['parameters'][1]['name']

    import re
    # ViViz assumes ID starting with http means configuration is obtained from that address
    serverx = re.sub(r"https*://", "", server) 

    #vivizhash = "catalog=" + server + "/" + dataset0 + gid
    if dataset is None:
        vivizhash = "catalog=" + "" + server + "/" + dataset0 + gid
    else:
        vivizhash = "catalog=" + server + "/" + dataset0 + gid

    return indexhtm_hash, vivizhash


def adddatasets(server, datasets, indexjs, **kwargs):
    import os
    import re
    import json
    from hapiclient.hapi import hapi, hapitime2datetime, server2dirname

    if kwargs['loglevel'] == 'debug':
        log('hapiplotserver.viviz.adddataset(): Appending to ' + indexjs)

    s = ''
    # ViViz assumes ID starting with http means configuration is obtained from that address
    serverx = re.sub(r"https*://", "", server) 
    for dataset, meta in datasets.items():
        s = s + '\nVIVIZ["config"]["catalogs"]["%s/%s"] = {"URL": ""};\n' % (server, dataset)
        s = s + 'VIVIZ["catalogs"]["%s/%s"] = \n' % (server, dataset)
        #s = s + '\nVIVIZ["config"]["catalogs"]["a/%s"] = {"URL": ""};\n' % (dataset)
        #s = s + 'VIVIZ["catalogs"]["a/%s"] = \n' % (dataset)

        gallery = {
                     'id': server,
                     'aboutlink': server,
                     'strftime':  strftime_str(meta),
                     'start': adjust_time(meta['startDate'], 1),
                     'stop': adjust_time(meta['stopDate'], -1),
                     'fulldir': ''
                    }

        galleries = []
        for parameter in meta['parameters']:
            p = parameter['name']
            fulldir = "../?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=svg&"
            thumbdir = "../?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=svg&"
            galleryc = gallery.copy()
            galleryc['fulldir'] = fulldir
            galleryc['thumbdir'] = thumbdir
            galleryc['id'] = p
            galleryc['aboutlink'] = server + "/info?id=" + dataset
            galleries.append(galleryc)

        s = s + json.dumps(galleries, indent=4) + "\n"

    if kwargs['loglevel'] == 'debug':
        log('hapiplotserver.viviz.adddataset(): Appending to ' + indexjs)
    with open(indexjs, 'a') as f:
        f.write(s)


def adddataset(server, dataset, indexjs, **kwargs):

    import os
    import json
    from hapiclient.hapi import hapi, hapitime2datetime, server2dirname

    fname = server2dirname(server) + '/' + dataset + '.json'
    catalogabs = kwargs['cachedir'] + '/viviz/catalogs/' + fname
    catalogrel = 'catalogs/' + fname

    dname = os.path.dirname(catalogabs)
    if not os.path.exists(dname):
        os.makedirs(dname)

    if kwargs['loglevel'] == 'debug':
        log('hapiplotserver.viviz.adddataset(): Appending to ' + indexjs)

    with open(indexjs, 'a') as f:
        f.write('\nVIVIZ["config"]["catalogs"]["%s/%s"] = {};\n' % (server, dataset))

    with open(indexjs, 'a') as f:
        f.write('VIVIZ["config"]["catalogs"]["%s/%s"]["URL"] = "%s";\n' % (server, dataset, catalogrel))

    if False and os.path.exists(catalogabs):
        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.viviz.adddataset(): Using cached ' + catalogabs)
        return

    try:
        opts = {'logging': True}
        meta = hapi(server, dataset, **opts)
    except Exception as e:
        log(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        print(message)


    gallery = {
                 'id': server,
                 'aboutlink': server,
                 'strftime': strftime_str(meta),
                 'start': adjust_time(meta['startDate'], 1),
                 'stop': adjust_time(meta['stopDate'], -1),
                 'fulldir': ''
                }

    galleries = []
    for parameter in meta['parameters']:
        p = parameter['name']
        fulldir = "../?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=svg&"
        thumbdir = "../?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=svg&"
        galleryc = gallery.copy()
        galleryc['fulldir'] = fulldir
        galleryc['thumbdir'] = thumbdir
        galleryc['id'] = p
        galleryc['aboutlink'] = server + "/info?id=" + dataset
        galleries.append(galleryc)

    if kwargs['loglevel'] == 'debug':
        log('hapiplotserver.viviz.vivizconfig(): Writing ' + catalogabs)

    with open(catalogabs, 'w') as f:
        json.dump(galleries, f, indent=4)


def strftime_str(meta):

    import isodate

    strftime = "time.min=$Y-$m-$dT00:00:00.000Z&time.max=$Y-$m-$dT23:59:59.999Z"
    if 'cadence' in meta:
        td = isodate.parse_duration(meta["cadence"])
        cadence = td.seconds + td.microseconds/1e6
        if cadence <= 0.01:      # cadence <= 0.01 second                   => 1 minute increments
            strftime = "time.min=$Y-$m-$dT$H:$M:00.000Z&time.max=$Y-$m-$dT$H:$M:59.999Z"
        elif cadence <= 0.1:     # 0.01 second  < cadence <= 0.1 second   => 1 minute increments
            strftime = "time.min=$Y-$m-$dT$H:$M:00.000Z&time.max=$Y-$m-$dT$H:$M:59.999Z"
        elif cadence <= 10:   # 0.1 second  < cadence <= 10 seconds      => 1 hour increments
            strftime = "time.min=$Y-$m-$dT$H:00:00.000Z&time.max=$Y-$m-$dT$H:59:59.999Z"
        elif cadence <= 60:   # 10 seconds < cadence <= 1 minute         => 1 day increments
            strftime = "time.min=$Y-$m-$dT00:00:00.000Z&time.max=$Y-$m-$dT23:59:59.999Z"
        elif cadence <= 60*10:  # 1 minute < cadence <= 10 minute        => 2 day increments
            strftime = "time.min=$Y-$m-${d;delta=2}T00:00:00.000Z&time.max=${Y;offset=0}-${m;offset=0}-${d;offset=2}T00:00:00.000Z"
        elif cadence <= 60*60:  # 10 minute < cadence <= 60 minute        => 10 day increments
            strftime = "time.min=$Y-$m-${d;delta=10}T00:00:00.000Z&time.max=${Y;offset=0}-${m;offset=0}-${d;offset=10}T00:00:00.000Z"
        elif cadence <= 60*60*24: # 60 minute < cadence <= 1 day         => 30 day increments
            strftime = "time.min=$Y-$m-${d;delta=30}T00:00:00.000Z&time.max=${Y;offset=0}-${m;offset=0}-${d;offset=30}T00:00:00.000Z"
        else: # cadence > 1 day                                             => 1 year increments
            strftime = "time.min=$Y-$m-${d;delta=365}T00:00:00.000Z&time.max=${Y;offset=365}-${m;offset=365}-${d;offset=365}T00:00:00.000Z"

    print(strftime)
    return strftime    


def adjust_time(hapitime, ndays):
    """Convert HAPI Time to %Y-%m-%d and add +/1 day"""

    from datetime import datetime, date, timedelta
    from hapiclient import hapitime2datetime

    dt = hapitime2datetime(hapitime)[0]
    if dt.strftime('%Y-%m-%dT%H:%M:%D.%f') != dt.strftime('%Y-%m-%dT00:00:00.000000'):
        dt = datetime.date(dt) + timedelta(days=ndays)

    # The following is needed as it will convert startDate in YYYY-DOY
    # format to YYYY-MM-DD, which ViViz only handles.
    time_string = dt.strftime('%Y-%m-%d')
    return time_string
