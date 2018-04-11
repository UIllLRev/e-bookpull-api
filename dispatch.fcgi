#!/usr/bin/python

from config import do_config
do_config()

from fcgi import WSGIServer
from e_bookpull_api import app

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = '/'.join(environ['SCRIPT_NAME'].split('/')[:-1])
       return self.app(environ, start_response)

app.wsgi_app = ScriptNameStripper(app.wsgi_app)

if __name__ == '__main__':
    WSGIServer(app.wsgi_app).run()
