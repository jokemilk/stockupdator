#!/usr/env python
# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.ext import ndb
from database import stockbooker
import logging

root_key = ndb.Key('stockbooker', 'root')

#handle mail request and do replay
#what i need ?

#in request we can do
#1.list all subscribed stocks
#2.subscribe a stock
#3.unsubscribe a stock
#4.delete the account/if there is no subed stock, delete it also

#we will reply
#list all in db as reply
#list the result for request

def listall(mailaddr):
    logging.info(mailaddr)
    sk = stockbooker.query(stockbooker.mailaddr == mailaddr,ancestor=root_key).fetch()
    if len(sk) == 1:
        return sk[0].stocklist.split()
    else:
        logging.error("no mailaddr")
        return None

def addstock(mailaddr,stock):
    logging.info(mailaddr)
    sk = stockbooker.query(stockbooker.mailaddr == mailaddr,ancestor=root_key).fetch()
    if len(sk) == 1:
        if stock in sk[0].stocklist:
            logging.error("stock already exist in list")
            return
        else:
            sk[0].stocklist = sk[0].stocklist + ' ' + stock
            sk[0].put()
    elif len(sk) == 0:
        sk = stockbooker(parent=root_key,mailaddr = mailaddr,stocklist = stock)
        res=sk.put()
    else:
        logging.error("no mailaddr or dup mailaddr")

def rmstock(mailaddr,stock):
    logging.info(mailaddr)
    logging.info(stock)
    sk = stockbooker.query(stockbooker.mailaddr == mailaddr,ancestor=root_key).fetch()
    if len(sk) == 1:
        if stock in sk[0].stocklist:
            ls = sk[0].stocklist.split()
            ls.remove(stock)
            if 0 == len(ls):
                sk[0].key.delete()
                return
            sk[0].stocklist = ' '.join(ls)
            sk[0].put()
        else:
            logging.error("stock doesn't exist in list")
    else:
        logging.error("no mailaddr")

def unsub(mailaddr):
    logging.info(mailaddr)
    sk = stockbooker.query(stockbooker.mailaddr == mailaddr,ancestor=root_key).fetch()
    if len(sk) == 1:
        sk[0].key.delete()
    else:
        logging.error("no mailaddr")

class EmailHandler(webapp.RequestHandler):
	def post(self):
		logging.info("mail recieved!")
		message = mail.InboundEmailMessage(self.request.body)
                sender = message.sender
                content=""
                #get mail content
                for body in message.bodies(content_type='text/plain'):
                    content += body[1].decode().encode()
                content = content.strip().split("\n")
                for line in content:
                    ll=line.strip().split()
                    if ll[0] == 'add' and len(ll) > 1 :
                        addstock(sender,ll[1]) 
                    elif ll[0] == 'remove' and len(ll) > 1:
                        rmstock(sender,ll[1])
                    elif ll[0] == 'unsubscribe':
                        unsub(sender)
                #reply all sub stock in mail
                logging.info(listall(sender))

		
app = webapp.WSGIApplication([('/_ah/mail/.+', EmailHandler)],debug=True)
if __name__ == '__main__':
    run_wsgi_app(app)

