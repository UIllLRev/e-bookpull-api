#!/usr/bin/python -O

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

from e_bookpull_api import app
from e_bookpull_api.import_route import ImportRoute
from e_bookpull_api.upload_route import UploadRoute
import_route = ImportRoute(app)
upload_route = UploadRoute(app, os.environ['UPLOAD_DIR'], os.environ['UPLOAD_PATH'])

# Configure Sentry
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from raven import fetch_git_sha
sentry_sdk.init(
        integrations=[FlaskIntegration()],
        release=fetch_git_sha(os.path.dirname(__file__)),
        environment = app.config['ENV']
        )


# TODO: determine if Sentry integration with Flask logging
# is a better way to do this
from werkzeug.exceptions import HTTPException
@app.errorhandler(HTTPException)
def send_http_errors_to_sentry(e):
    sentry_sdk.capture_exception(e)
    return e.get_response(), e.code

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       # Both Flask's jsonify and Flask-REST-JSONAPI add a Content-Type header.
       # This is a quick and easy hack to suppress duplicate headers.
       def real_start_response(status, headers):
           headers = set(headers)
           return start_response(status, headers)
       environ['SCRIPT_NAME'] = '/'.join(environ['SCRIPT_NAME'].split('/')[:-1])
       return self.app(environ, real_start_response)

app.wsgi_app = ScriptNameStripper(app.wsgi_app)

if __name__ == '__main__':
    from fcgi import WSGIServer
    class MyWSGIServer(WSGIServer):
        def error(self, req):
            """
            Override default implementation which prints a traceback.
            """
            req.stdout.write('Content-Type: application/vnd.api+json\r\n\r\n{"errors": [{"status": "500", "detail": "Unknown error.", "title": "Unknown Error"}],"jsonapi": {"version": "1.0"}}')

    MyWSGIServer(app.wsgi_app).run()
