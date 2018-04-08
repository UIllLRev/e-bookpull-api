#!/home/ilr_dev/dev.illinoislawreview.org/members/apiv2/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy import Column, Date, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import ENUM

from werkzeug.wrappers import Response

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

@app.after_request
def add_cors_headers(response):
    if (app.config['DEBUG']):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
    return response

class Work(db.Model):
    __tablename__ = 'works'
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}
    author_code = Column(Integer, primary_key=True)
    author_name = Column(String(80))
    article_name = Column(Text)
    volume = Column(SmallInteger)
    issue = Column(SmallInteger)
    comments = Column(Text)
    bookpuller = Column(Text)
    duedate = Column(Date)

class Source(db.Model):
    __tablename__ = 'sources'
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}
    id = Column(Integer, primary_key=True)
    author_code = Column(Integer, ForeignKey('works.author_code'), nullable=False)
    type = Column(ENUM('B', 'C', 'J', 'L', 'M', 'P'), index=True)
    citation = Column(Text)
    url = Column(Text)
    comments = Column(Text)
    ordered = Column(Date)
    status_code = Column(ENUM('N', 'E', 'M', 'R', 'X', 'XP', 'XR'), index=True)
    work = db.relationship('Work', backref=db.backref('sources'))

db.create_all()

# Create schema
class WorkSchema(Schema):
    class Meta:
        type_ = 'work'
        self_view = 'work_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'work_list'

    id = fields.Integer(as_string=True, dump_only=True, attribute='author_code')
    author = fields.Str(attribute='author_name', allow_none=True)
    title = fields.Str(attribute='article_name', allow_none=True)
    volume = fields.Integer(as_string=True, allow_none=True)
    issue = fields.Integer(as_string=True, allow_none=True)
    comments = fields.Str(allow_none=True)
    bookpuller = fields.Str(allow_none=True)
    sources = Relationship(self_view='work_sources',
            self_view_kwargs={'id': '<author_code>'},
            related_view='source_list',
            related_view_kwargs={'id': '<author_code>'},
            many=True,
            schema='SourceSchema',
            type_='source')

# Create resource managers
class WorkList(ResourceList):
    schema = WorkSchema
    data_layer = {'session': db.session,
                  'model': Work}

class WorkDetail(ResourceDetail):
    schema = WorkSchema
    data_layer = {'session': db.session,
                  'model': Work}

class WorkSourcesRelationship(ResourceRelationship):
    schema = WorkSchema 
    data_layer = {'session': db.session,
                  'model': Work}
# Create schema
class SourceSchema(Schema):
    class Meta:
        type_ = 'source'
        self_view = 'source_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'source_list'

    id = fields.Integer(as_string=True, dump_only=True)
    work = fields.Integer(as_string=True, dump_only=True, attribute='author_code')
    type = fields.Str()
    citation = fields.Str()
    url = fields.Str(allow_none=True)
    comments = fields.Str(allow_none=True)
    ordered = fields.Date(allow_none=True)
    status = fields.Str(attribute='status_code')

# Create resource managers
class SourceList(ResourceList):
    def query(self, view_kwargs):
        if view_kwargs.get('id') is not None:
            return self.session.query(Source).filter_by(author_code=view_kwargs['id'])
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

# Start the flask loop
if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
