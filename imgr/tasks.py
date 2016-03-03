# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import Celery
from datetime import timedelta
import os
from pymongo import MongoClient

# instantiate Celery object
mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
app = Celery(include=[ 'imgr.tasks' ], broker=mongourl + 'celery')
app.config_from_object('imgr.celeryconfig')

client = MongoClient(host=mongourl + 'imgr', connect=False)
db = client['imgr']

@app.task
def syncfs(path):
    import os
    from glob import glob
    from itertools import chain
    
    col = db['files']

    filelist = (chain.from_iterable(glob(os.path.join(x[0], '*.*')) for x in os.walk(path)))
    for filename in filelist:
        
        fdoc = col.find_one({'name': filename})
        
        # if file is not in db, add it
        if not fdoc:
            fdoc = { 'name': filename,
                     'del': False,
                     'meta': {} }

            col.insert_one(fdoc)
            continue

        # if file is in db, and 'remove' tag is true, remove file
        if fdoc['del'] == True:
            os.remove(filename)
            col.delete_one(fdoc)

if __name__ == '__main__':
    app.start()