from hapiplotserver.log import log


def getviviz(**kwargs):
    """Download ViViz web application"""

    import os
    import zipfile
    import requests

    vivizdir = kwargs['cachedir'] + "/viviz"

    if not os.path.exists(vivizdir):
        url = 'https://github.com/rweigel/viviz/archive/master.zip'

        if kwargs['loglevel'] == 'debug':
            log('hapiplotserver.viviz(): Downloading ' + url + ' to ' + kwargs['cachedir'])

        file = kwargs['cachedir'] + '/viviz-master.zip'

        r = requests.get(url, allow_redirects=True)
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
    """Convert HAPI request parameters to santized string for part of file name"""

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

    indexjs_rel = 'viviz/index-' + slug + '.js'
    indexjs = kwargs['cachedir'] + '/' + indexjs_rel
    indexjso = kwargs['cachedir'] + '/viviz/index.js'
    shutil.copyfile(indexjso, indexjs)
    print('hapiplotserver.viviz.vivizconfig(): Wrote %s' % indexjs)

    indexhtm = kwargs['cachedir'] + '/viviz/index-' + slug + '.htm'
    indexhtmo = kwargs['cachedir'] + '/viviz/index.htm'
    shutil.copyfile(indexhtmo, indexhtm)
    log('hapiplotserver.viviz.vivizconfig(): Wrote %s' % indexhtm)

    fid = hashlib.md5(bytes(slug, 'utf8')).hexdigest()
    indexhtm_hash = kwargs['cachedir'] + '/viviz/' + fid[0:4]
    if os.path.isfile(indexhtm_hash):
        os.remove(indexhtm_hash)
        log('hapiplotserver.viviz.vivizconfig(): Removed existing %s' % indexhtm_hash)

    log('hapiplotserver.viviz.vivizconfig(): Symlinking %s with %s' % (indexhtm, indexhtm_hash))
    os.symlink(indexhtm, indexhtm_hash)
    indexhtm_hash = fid[0:4]

    indexjs_rel = 'index-' + slug + '.js'
    with open(indexhtm) as f:
        tmp = f.read().replace('<script type="text/javascript" src="index.js',
                               '<script type="text/javascript" src="' + indexjs_rel)
    with open(indexhtm, "w") as f:
        f.write(tmp)

    if dataset is None:
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
        gid = "&id=" + parameters.split(",")[0]
    else:
        if dataset is not None:
            meta = hapi(server, dataset0)
            # Set first parameter shown to be first in dataset (if this is
            # not done the time variable is the first parameter shown, which
            # is generally not wanted.)
            gid = "&id=" + meta['parameters'][1]['name']

    vivizhash = "catalog=" + server + "/" + dataset0 + gid

    return indexhtm_hash, vivizhash


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

    meta = hapi(server, dataset)

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

    gallery = {
                 'id': server,
                 'aboutlink': server,
                 'strftime': "time.min=$Y-$m-$dT00:00:00.000Z&time.max=$Y-$m-$dT23:59:59.999Z",
                 'start': adjust_time(meta['startDate'], 1),
                 'stop': adjust_time(meta['stopDate'], -1),
                 'fulldir': ''
                }

    galleries = []
    for parameter in meta['parameters']:
        p = parameter['name']
        fulldir = "../?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=png&"
        thumbdir = "../?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=png&dpi=72&"
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
