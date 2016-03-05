# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import Celery
from datetime import timedelta
import os
from pymongo import MongoClient
from celery.utils.log import get_task_logger

# init celery
logger = get_task_logger(__name__)
mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
app = Celery(include=[ 'imgr.tasks' ], broker=mongodb_url + 'celery')
app.config_from_object('imgr.celeryconfig')

client = MongoClient(host=mongodb_url + 'imgr')
db = client['imgr']

@app.task
def syncfs(path):
    import os
    from glob import glob
    from itertools import chain
    import uuid
    import re
    import mimetypes as mt
    
    col = db['files']

    filelist = (chain.from_iterable(glob(os.path.join(x[0], '*.*')) for x in os.walk(path)))
    for filename in filelist:
        
        fname = re.sub(path, '', filename)
        ftype = mt.guess_type(fname)
        if ftype[0] is None:
            # ignore unrecognized file
            logger.warn('Unrecognized file [{0}]!'.format(fname))
            continue

        fdoc = col.find_one({'name': fname})
        
        # if file is not in db, add it
        if not fdoc:
            fdoc = {'_id': str(uuid.uuid4()),
                    'name': fname,
                    'type': ftype[0],
                    'del': False,
                    'meta': {} }

            logger.info('Inserting new file [{0}]...'.format(fname))
            col.insert(fdoc)
            continue

        # if file is in db, and 'remove' tag is true, remove file
        if fdoc['del'] == True:
            logger.info('Removing file [{0}]...'.format(fname))
            os.remove(path + fname)
            col.remove(fdoc)

if __name__ == '__main__':
    app.start()