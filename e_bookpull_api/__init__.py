#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from flask_sqlalchemy import SQLAlchemy

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# This is deprecated apparently. Set to suppress warning.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Flask's jsonify appends a Content-Type. Make it the right one.
app.config['JSONIFY_MIMETYPE'] = 'application/vnd.api+json'
# Set a large page size so we (generally) get all our data in one call.
app.config['PAGE_SIZE'] = 500
db = SQLAlchemy(app)

from models import Work, Source
from schemas import WorkSchema, SourceSchema
db.create_all()

@app.after_request
def add_cors_headers(response):
    if (app.config['DEBUG']):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE, GET, OPTIONS, PATCH, POST, PUT')
    return response


# Create resource managers
class WorkList(ResourceList):
    schema = WorkSchema
    data_layer = {'session': db.session,
                  'model': Work}

class WorkDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('source_id') is not None:
            try:
                source = self.session.query(Source).filter_by(id=view_kwargs['source_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'source_id'},
                                     "Source: {} not found".format(view_kwargs['source_id']))
            else:
                if source.work is not None:
                    view_kwargs['id'] = source.work.id
                else:
                    view_kwargs['id'] = None

    schema = WorkSchema
    data_layer = {'session': db.session,
                  'model': Work,
                  'methods': {'before_get_object': before_get_object}}

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
                  'methods': {'query': query}}

class SourceDetail(ResourceDetail):
    schema = SourceSchema
    data_layer = {'session': db.session,
                  'model': Source}

class SourceWorkRelationship(ResourceRelationship):
    schema = SourceSchema
    data_layer = {'session': db.session,
                  'model': Source}

# Create the API object
api = Api(app)
api.route(WorkList, 'work_list', '/works')
api.route(WorkDetail, 'work_detail', '/works/<int:id>', '/sources/<int:source_id>/work')
api.route(WorkSourcesRelationship, 'work_sources', '/works/<int:id>/relationships/sources')
api.route(SourceList, 'source_list', '/sources', '/works/<int:id>/sources')
api.route(SourceDetail, 'source_detail', '/sources/<int:id>')
api.route(SourceWorkRelationship, 'source_work', '/sources/<int:id>/relationships/work')
