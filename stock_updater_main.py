#!/usr/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.labs import taskqueue
from google.appengine.ext import ndb
from database import client_db
import logging

root_key = ndb.Key('client_db', 'root')

class  UpdaterHandler(webapp.RequestHandler):
	def get(self):
                #read data base and get client/stocks
                records = client_db.query(ancestor=root_key)
                #for each client add a taskqueue
                for r in records:
                    taskqueue.add(params={'client': r.mail , 'stocks' : r.stocklist})
		
app = webapp.WSGIApplication([('/stock_updater', UpdaterHandler)],
                                     debug=True)
if __name__ == '__main__':
    run_wsgi_app(app)

