from flask import request 
from models import Work, Source
from . import db
import json

class ImportRoute:
    def __init__(self, app): 
        @app.route('/import/<int:work_id>', methods=['POST'])
        def import_route(work_id):
            if 'file' in request.files:
                work = Work.query.get(work_id)
                f = request.files['file']
                sources = json.load(f)
                for source in sources:
                    s = Source(work_id=work.id, type=source["type"], citation=source["citation"])
                    db.session.add(s)
                db.session.commit()
                return '', 204
            return json.dumps({
                "errors": [{"status": "400", "detail": "No file named 'file' in request.", "title": "Bad request"}],
                "jsonapi": {"version": "1.0"}
                }), 400, {"Content-Type": "application/vnd.api+json"}
