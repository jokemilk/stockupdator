#!/usr/env python
# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.ext import ndb
from database import client_db
import logging

root_key = ndb.Key('client_db', 'root')

#handle mail request and do replay

#in request we can do
#1.list all subscribed stocks
#2.subscribe a stock
#3.unsubscribe a stock
#4.delete the account/if there is no subed stock, delete it also

def listall(client):
    records = client_db.query(client_db.mail == client,ancestor=root_key).fetch()
    if len(records) == 1:
        return "client:"+client+"; stock list: "+records[0].stocklist
    else:
        logging.error("listall error: client not exist")
        return None

def addstock(client,stock):
    records = client_db.query(client_db.mail == client,ancestor=root_key).fetch()
    if len(records) == 1:
        if stock in records[0].stocklist:
            logging.warn("addstock warning: stock already exist in list")
            return
        else:
            records[0].stocklist = records[0].stocklist + ' ' + stock
            records[0].put()
            logging.info("client %s add stock %s" %(client,stock))
    elif len(records) == 0:
        records = client_db(parent=root_key,mail = client,stocklist = stock)
        res=records.put()
    else:
        logging.error("addstock error: client not exist or dup")

def rmstock(client,stock):
    records = client_db.query(client_db.mail == client,ancestor=root_key).fetch()
    if len(records) == 1:
        if stock in records[0].stocklist:
            ls = records[0].stocklist.split()
            ls.remove(stock)
            if 0 == len(ls):
                records[0].key.delete()
                return
            records[0].stocklist = ' '.join(ls)
            records[0].put()
            logging.info("client %s rm stock %s" %(client,stock))
        else:
            logging.warn("rmstock warning: stock doesn't exist in list")
    else:
        logging.error("rmstock error: client not exist")

def unsub(client):
    records = client_db.query(client_db.mail == client,ancestor=root_key).fetch()
    if len(records) == 1:
        records[0].key.delete()
        logging.info("client %s deleted" %(client))
    else:
        logging.error("unsub error: client not exist")

class EmailHandler(webapp.RequestHandler):
	def post(self):
		message = mail.InboundEmailMessage(self.request.body)
                sender = message.sender
                logging.info("mail recieved! %s" %(sender))
                content=""
                #get mail content
                for body in message.bodies(content_type='text/plain'):
                    content += body[1].decode().encode()
                content = content.strip().split("\n")
                for line in content:
                    cmd = line.strip().split()
                    if cmd[0] == 'add' and len(cmd) > 1 :
                        addstock(sender,cmd[1]) 
                    elif cmd[0] == 'rm' and len(cmd) > 1:
                        rmstock(sender,cmd[1])
                    elif cmd[0] == 'unsub':
                        unsub(sender)
                #reply all sub stock in mail
                logging.info(listall(sender))

		
app = webapp.WSGIApplication([('/_ah/mail/.+', EmailHandler)],debug=True)
if __name__ == '__main__':
    run_wsgi_app(app)

