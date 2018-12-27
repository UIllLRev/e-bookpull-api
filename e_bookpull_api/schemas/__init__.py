from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

# Create schema
class WorkSchema(Schema):
    class Meta:
        type_ = 'work'
        self_view = 'work_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'work_list'

    id = fields.Integer(as_string=True, dump_only=True)
    author = fields.Str(attribute='author_name', allow_none=True)
    title = fields.Str(attribute='article_name', allow_none=True)
    volume = fields.Integer(as_string=True, allow_none=True)
    issue = fields.Integer(as_string=True, allow_none=True)
    comments = fields.Str(allow_none=True)
    bookpuller = fields.Str(allow_none=True)
    sources = Relationship(self_view='work_sources',
            self_view_kwargs={'id': '<id>'},
            related_view='source_list',
            related_view_kwargs={'id': '<id>'},
            many=True,
            schema='SourceSchema',
            type_='source')

# Create schema
class SourceSchema(Schema):
    class Meta:
        type_ = 'source'
        self_view = 'source_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'source_list'

    id = fields.Integer(as_string=True, dump_only=True)
    type = fields.Str()
    citation = fields.Str()
    url = fields.Str(allow_none=True)
    comments = fields.Str(allow_none=True)
    ordered = fields.Date(allow_none=True)
    status = fields.Str(attribute='status_code')
    work = Relationship(self_view='source_work',
            self_view_kwargs={'id': '<id>'},
            related_view='work_detail',
            related_view_kwargs={'source_id': '<id>'},
            schema='WorkSchema',
            type_='work')
