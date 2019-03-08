def prepviviz(server, dataset, **kwargs):
    """Prepare ViViz web application"""

    import os
    vivizdir = kwargs['cachedir'] + "/viviz"

    if not os.path.exists(vivizdir):
        if kwargs['loglevel'] == 'debug':
            print('hapiplotserver.app(): Downloading ViViz to ' + kwargs['cachedir'])
        getviviz(**kwargs)
    else:
        if kwargs['loglevel'] == 'debug':
            print('hapiplotserver.app(): Found ViViz at ' + vivizdir)

    vivizconfig(server, dataset, **kwargs)

def getviviz(**kwargs):
    """Download ViViz web application"""

    import shutil
    import zipfile
    from hapiclient.util import system, download

    url = 'https://github.com/rweigel/viviz/archive/master.zip'
    file = kwargs['cachedir'] + '/viviz-master.zip'
    if shutil.which('git'):
        code, stderr, stdout = system('git clone https://github.com/rweigel/viviz.git ' + kwargs['cachedir'] + '/viviz')
        if kwargs['loglevel'] == 'debug':
            print(code, stderr, stdout)
    else:
        download(file, url)
        zipref = zipfile.ZipFile(file, 'r')
        zipref.extractall(kwargs['cachedir'])
        zipref.close()


def vivizconfig(server, dataset, **kwargs):
    """Create ViViz configuration catalog"""

    import os
    import json
    import shutil
    from hapiclient.hapi import hapi, server2dirname

    indexjs = kwargs['cachedir'] + '/viviz/index.js'

    fname = server2dirname(server) + '_' + dataset + '.json'
    catalogabs = kwargs['cachedir'] + '/viviz/catalogs/' + fname
    catalogrel = 'catalogs/' + fname

    meta = hapi(server, dataset)

    gallery = {
                'id': server,
                 'aboutlink': server,
                 'strftime': "time.min=$Y-$m-$dT00:00:00.000Z&time.max=$Y-$m-$dT23:59:59.999Z",
                 'start': meta['startDate'],
                 'stop': meta['stopDate'],
                 'fulldir': ''
                }

    galleries = []
    for parameter in meta['parameters']:
        p = parameter['name']
        fulldir = "/?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=png&"
        thumbdir = "/?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(kwargs['usecache']).lower() + "&format=png&dpi=72&"
        galleryc = gallery.copy()
        galleryc['fulldir'] = fulldir
        galleryc['thumbdir'] = thumbdir
        galleryc['id'] = p
        galleryc['aboutlink'] = server + "/info?id=" + dataset
        galleries.append(galleryc)

    indexjs_original = indexjs.replace(".js","-original.js")
    if not os.path.isfile(indexjs_original):
        shutil.copyfile(indexjs, indexjs_original)
    else:
        shutil.copyfile(indexjs_original, indexjs)

    dname = os.path.dirname(catalogabs)
    if not os.path.exists(dname):
        os.makedirs(dname)

    if kwargs['loglevel'] == 'debug':
        print('hapiplotserver.catalog(): Writing ' + catalogabs)

    with open(catalogabs, 'w') as f:
        json.dump(galleries, f, indent=4)

    if kwargs['loglevel'] == 'debug':
        print('hapiplotserver.catalog(): Appending to ' + indexjs)

    with open(indexjs,'a') as f:
        f.write('\nVIVIZ["config"]["catalogs"]["%s"] = {};\n' % server)

    with open(indexjs,'a') as f:
        f.write('VIVIZ["config"]["catalogs"]["%s"]["URL"] = "%s";\n' % (server, catalogrel))
