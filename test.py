#!/usr/bin/python

import imp

dispatch = imp.load_source('dispatch', './dispatch.fcgi')

dispatch.app.config['DEBUG'] = True
dispatch.app.run()
