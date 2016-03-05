# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application, RequestHandler, HTTPError
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.options import define, options
from tornado.gen import coroutine, Return
import motor
import json
import re
import os

base_url = 'http://' + os.getenv('OPENSHIFT_GEAR_DNS', 'localhost:8080')

class FileHandler(RequestHandler):

    @coroutine
    def post(self, uuid):
        client = AsyncHTTPClient()
        regex = re.compile('[a-f0-9]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', re.I)
        if not regex.match(uuid):
            raise HTTPError(400, 'Invalid uuid')
            
        delete = self.get_argument('del', None)
        if delete:
            req = HTTPRequest(url=base_url + '/files/{id}'.format(id=uuid), method='DELETE')
            res = yield client.fetch(req)
            yield self.redirect(base_url)
            return

        metakey = self.get_body_arguments('key')
        metaval = self.get_body_arguments('val')

        if len(metakey) and len(metakey[0]):
            body = {'key': metakey[0], 'val': metaval[0]}
            req = HTTPRequest(url=base_url + '/files/{id}'.format(id=uuid), body=json.dumps(body), method='PUT')
            res = yield client.fetch(req)   

        yield self.get(uuid)   

    @coroutine
    def get(self, uuid):
        client = AsyncHTTPClient()
        regex = re.compile('[a-f0-9]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', re.I)
        if not regex.match(uuid):
            raise HTTPError(400, 'Invalid uuid')

        res = yield client.fetch(base_url + '/files/{id}'.format(id=uuid))
        res = json.loads(res.body)

        meta = []
        if len(res) <= 0:
            filename = 'File not found!'
            filetype = None
        else:
            file = res['files'][0]
            filename = file['name']
            filetype = file['type']

            for m, val in file['meta'].iteritems():
                meta.append('{mkey}: {mval}'.format(mkey=m, mval=val))      

        self.render("file.html", title='File Description', meta=meta, filename=filename, filetype=filetype)      



class HomeHandler(RequestHandler):    

    @coroutine
    def post(self):
        query = self.get_argument('q')
        key = self.get_argument('k', None)
        if not key:
            key = 'name'
        else:
            key = 'meta.' + key

        client = AsyncHTTPClient()
        files = []

        res = yield client.fetch(base_url + '/files?q={q}&k={k}'.format(q=query, k=key))
        res = json.loads(res.body)
        files = res['files']

        yield self.get(files=files)

    @coroutine
    def get(self, files=None):
        if not files:
            files = []

        self.render("index.html", title='Image Bank', items=files)



class MainHandler(RequestHandler):
    
    def initialize(self, db):
        self.db = db
    
    @coroutine
    def get(self, uuid=None):
        col = self.db['files']
        
        if not uuid:
            query = self.get_argument('q')
            key = self.get_argument('k')
        else:
            query = uuid
            key = '_id'

        files = []

        cursor = col.find({key: {'$regex': query, '$options': 'si'}, 'del': False })            
        for file in (yield cursor.to_list(length=100)):
                files.append(file)

        res = {'status': 0,
                'files': files}
        self.write(res)

    @coroutine
    def put(self, uuid):
        # checking input
        regex = re.compile('[a-f0-9]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', re.I)
        if not regex.match(uuid):
            raise HTTPError(400, 'Invalid uuid')

        try:
            data = json.loads(self.request.body)
        except:
            raise HTTPError(400, 'Invalid body')            

        if 'key' not in data or 'val' not in data:
            raise HTTPError(400, 'Invalid body')            

        # updating file metadata
        res = { 'status': 0 }  
        
        col = self.db['files']
        upkey = 'meta.{0}'.format(data['key'])

        if data['val'] is None or len(data['val']) <= 0:
            doc = yield col.find_and_modify({ '_id': uuid }, { '$unset': { upkey: '' } } )
        else:
            doc = yield col.find_and_modify({ '_id': uuid, 'del': False }, { '$set': { upkey: data['val'] } } )

        if doc is None:
            res['status'] = 1
            res['message'] = 'File ID not found.'
        
        self.write(res)

    @coroutine
    def delete(self, uuid):
        # checking input
        regex = re.compile('[a-f0-9]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', re.I)
        if not regex.match(uuid):
            raise HTTPError(400, 'Invalid uuid')

        res = { 'status': 0 }  
        col = self.db['files']

        # delete file        
        doc = yield col.find_and_modify({ '_id': uuid }, { '$set': { 'del': True } } )

        if doc is None:
            res['status'] = 1
            res['message'] = 'File ID not found.'
        
        self.write(res)
        

def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=8080, help="Port")
    define("mongodb_url", default="127.0.0.1:27017", help="MongoDB connection URL")
    tornado.options.parse_command_line()

    client = motor.motor_tornado.MotorClient(options.mongodb_url)
    db = client['imgr']
    
    template_dir = os.getenv('OPENSHIFT_REPO_DIR', '')
    template_dir = os.path.join(template_dir, 'imgr/templates')
    static_dir = os.getenv('OPENSHIFT_DATA_DIR', os.path.dirname(__file__))
    static_dir = os.path.join(static_dir, 'static')

    settings = {
        "static_path": static_dir,
        'template_path': template_dir
    }

    application = Application([(r"/files/([^/]+)/?", MainHandler, dict(db=db)),
                                (r"/files/?", MainHandler, dict(db=db)),
                                (r'/?', HomeHandler, ), 
                                (r'/([^/]+)/?', FileHandler, )],
                                **settings)
    application.listen(options.port, options.host)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
