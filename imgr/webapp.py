# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application, RequestHandler, HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options
from tornado.gen import coroutine, Return
import motor
import json
import re
import os

class HomeHandler(RequestHandler):

    base_url = 'http://imgr-helderm.rhcloud.com'

    @coroutine
    def get(self):
        query = self.get_argument('q', None)
        key = self.get_argument('k', '')
        if len(key) <= 0:
            key = 'name'
        else:
            key = 'meta.' + key

        client = AsyncHTTPClient()
        files = []
        if query:
            res = yield client.fetch(self.base_url + '/files?q={q}&k={k}'.format(q=query, k=key))
            res = json.loads(res.body)

            for file in res['files']:
                files.append(file['name'])

        self.render("index.html", title='Image Bank', items=files)



class MainHandler(RequestHandler):
    
    def initialize(self, db):
        self.db = db
    
    @coroutine
    def get(self):
        col = self.db['files']
        query = self.get_argument('q')
        key = self.get_argument('k')
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

        # delete file        
        col = self.db['files']
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
    repo_dir = os.getenv('OPENSHIFT_REPO_DIR', '.')

    application = Application([(r"/files/([^/]+)", MainHandler, dict(db=db)),
                                (r"/files", MainHandler, dict(db=db)),
                                (r'/', HomeHandler, )], 
                                template_path=repo_dir + '/templates/')
    application.listen(options.port, options.host)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
