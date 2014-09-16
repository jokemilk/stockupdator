#!/usr/env python
# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
import logging

class EmailHandler(webapp.RequestHandler):
	def post(self):
		logging.info("mail recieved!")
		message = mail.InboundEmailMessage(self.request.body)
		logging.info(message)
		
app = webapp.WSGIApplication([('/_ah/mail/.+', EmailHandler)],debug=True)
if __name__ == '__main__':
    run_wsgi_app(app)

