from flask import request
from models import Work
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import errno
import json


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class UploadRoute:
    def __init__(self, app, upload_path): 
        @app.route('/upload/<int:work_id>', methods=['POST'])
        def upload(work_id):
            if 'file' in request.files:
                work = Work.query.get(work_id)
                if work:
                    f = request.files['file']
                    target_dir = os.path.join(upload_path, work.author_name)
                    root = os.path.commonprefix([os.path.abspath(target_dir), os.path.abspath(request.environ['SCRIPT_NAME'])])
                    mkdir_p(target_dir)
                    filename = os.path.join(target_dir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S_") + secure_filename(f.filename))
                    f.save(filename)
                    return json.dumps({"url": os.path.relpath(filename, root)}), 200, {"Content-Type": "application/vnd.api+json"}
                return json.dumps({
                    "errors": [{"status": "400", "detail": "Invalid work id.", "title": "Bad request"}],
                    "jsonapi": {"version": "1.0"}
                    }), 400, {"Content-Type": "application/vnd.api+json"}
            return json.dumps({
                "errors": [{"status": "400", "detail": "No file named 'file' in request.", "title": "Bad request"}],
                "jsonapi": {"version": "1.0"}
                }), 400, {"Content-Type": "application/vnd.api+json"}
