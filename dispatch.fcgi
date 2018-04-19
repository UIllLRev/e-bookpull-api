#!/usr/bin/python

# Load packages from our local directory
import sys
import os
base = os.path.dirname(os.path.abspath(__file__))
site_packages = os.path.join(base, 'lib', 'python%s' % sys.version[:3], 'site-packages')
import site
site.addsitedir(site_packages)

# Read configuration from .env
from dotenv import load_dotenv
load_dotenv()

# Configure Sentry
from e_bookpull_api import app
from e_bookpull_api.import_route import ImportRoute
from e_bookpull_api.upload_route import UploadRoute
from raven.contrib.flask import Sentry
import_route = ImportRoute(app)
upload_route = UploadRoute(app, os.environ['UPLOAD_PATH'])
sentry = Sentry(app)

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = '/'.join(environ['SCRIPT_NAME'].split('/')[:-1])
       return self.app(environ, start_response)

app.wsgi_app = ScriptNameStripper(app.wsgi_app)

if __name__ == '__main__':
    from fcgi import WSGIServer
    WSGIServer(app.wsgi_app).run()
