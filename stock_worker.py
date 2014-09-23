#!/usr/env python
# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.labs import taskqueue
from HTMLParser import HTMLParser
import logging

mock="http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/qgqp/index.phtml?symbol="

class MyParser(HTMLParser):
    def clear(self):
        self.Found = None
        self.recom = list() 
    def handle_starttag(self, tag, attrs):
        link_found = False
    #        print "Start tag:", tag
        for name,value in attrs:
    #        print "     attr:", attr
            if name == 'title' and value == u'点击查看该股历史千股千评':
                self.Found = 'advice'
                return
            if name == 'href' and 'http://biz.finance.sina.com.cn' in value:
                link_found = True
            if link_found and name == 'class' and value == 'keyword':
                self.Found = 'name'
    def handle_data(self, data):
    #        print "Data     :", data  
        if self.Found == 'name':
            self.recom.append(data)
#            print "Data     :", data
            self.Found = None
        elif self.Found == 'advice':
            self.recom.append(data)
            self.Found = None

MAX_RETRY = 3			
			
def get_stock_advices(stock_list):			
    content=''
    content.decode('gbk')
    for s in stock_list:
        logging.info(s)
        url = mock + s
  	retry = 0
	result = urlfetch.fetch(url,deadline=30)
  	while result.status_code != 200 and retry < MAX_RETRY:
 		result = urlfetch.fetch(url,deadline=30)
  	if result.status_code != 200:
 		logging.error("faild to fetch "+s)
 		continue
  	P = MyParser()
        P.clear()
        P.feed(result.content.decode('gbk'))
        recon = P.recom
        logging.info(recon)
        if 3 == len(recon):
            content += recon[1] + u': ' + recon[2] + u'\n\r'
        P.close()
    logging.info(content)
    return content			

from google.appengine.api import mail

def sendmail(receiver,content):
	mail.send_mail(sender="joemilu@gmail.com",
				  to=receiver,
				  subject=u"千股千评",
				  body=content)

	
class WorkerHandler(webapp.RequestHandler):
	def post(self):
                client_mail = self.request.get('mail')
                stock_list = self.request.get('stocks').split()
                logging.info(client_mail)
                logging.info(stock_list)
                #get content
                content = get_stock_advices(stock_list)
                if 0 != len(content):
		    sendmail(client_mail,content)
                    logging.info(content)
		
app = webapp.WSGIApplication([('/_ah/queue/default', WorkerHandler)],
                                     debug=True)
if __name__ == '__main__':
    run_wsgi_app(app)

