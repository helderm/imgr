# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import Celery
from datetime import timedelta
import os
from pymongo import MongoClient

# instantiate Celery object
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
    
    col = db['files']

    filelist = (chain.from_iterable(glob(os.path.join(x[0], '*.*')) for x in os.walk(path)))
    for filename in filelist:
        
        fname = re.sub(path, '', filename)
        fdoc = col.find_one({'name': fname})
        
        # if file is not in db, add it
        if not fdoc:
            fdoc = {'_id': str(uuid.uuid4()),
                    'name': fname,
                    'del': False,
                    'meta': {} }

            col.insert(fdoc)
            continue

        # if file is in db, and 'remove' tag is true, remove file
        if fdoc['del'] == True:
            os.remove(fname)
            col.delete_one(fdoc)

if __name__ == '__main__':
    app.start()