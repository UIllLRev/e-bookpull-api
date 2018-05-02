#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from flask_sqlalchemy import SQLAlchemy

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/vnd.api+json'
app.config['PAGE_SIZE'] = 500
db = SQLAlchemy(app)

from models import Work, Source
from schemas import WorkSchema, SourceSchema
db.create_all()

@app.after_request
def add_cors_headers(response):
    if (app.config['DEBUG']):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
    return response


# Create resource managers
class WorkList(ResourceList):
    schema = WorkSchema
    data_layer = {'session': db.session,
                  'model': Work}

class WorkDetail(ResourceDetail):
    schema = WorkSchema
    data_layer = {'session': db.session,
                  'model': Work}

    def before_delete(self, args, kwargs):
        obj = self._data_layer.get_object(kwargs)
        path = os.path.join(os.environ['UPLOAD_DIR'], obj.author_name)
        if os.path.isdir(path):
            os.rename(path, path + '.deleted')

class WorkSourcesRelationship(ResourceRelationship):
    schema = WorkSchema 
    data_layer = {'session': db.session,
                  'model': Work}

# Create resource managers
class SourceList(ResourceList):
    def query(self, view_kwargs):
        if view_kwargs.get('id') is not None:
            return self.session.query(Source).filter_by(work_id=view_kwargs['id'])
        return self.session.query(Source)

    schema = SourceSchema
    data_layer = {'session': db.session,
                  'model': Source,
                  'methods': {'query': query}
                  }

class SourceDetail(ResourceDetail):
    schema = SourceSchema
    data_layer = {'session': db.session,
                  'model': Source}

# Create the API object
api = Api(app)
api.route(WorkList, 'work_list', '/works')
api.route(WorkDetail, 'work_detail', '/works/<int:id>')
api.route(WorkSourcesRelationship, 'work_sources', '/works/<int:id>/relationships/sources')
api.route(SourceList, 'source_list', '/sources', '/works/<int:id>/sources')
api.route(SourceDetail, 'source_detail', '/sources/<int:id>')
