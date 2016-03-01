from celery import Celery

app = Celery('tasks')
app.config_from_object('celeryconfig')

from pymongo import MongoClient
client = MongoClient()
db = client['imgr']

@app.task
def list(path):
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
