#!/usr/env python
# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.labs import taskqueue
from HTMLParser import HTMLParser
from google.appengine.api import mail
import logging

mock="http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/qgqp/index.phtml?symbol="

class MyParser(HTMLParser):
    def clear(self):
        self.Found = None
        self.advice = list() 
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
        if self.Found == 'name':
            self.advice.append(data)
            self.Found = None
        elif self.Found == 'advice':
            self.advice.append(data)
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
        advice = P.advice
        logging.info(advice)
        if 3 == len(advice):
            content += advice[1] + u': ' + advice[2] + u'\n'
        P.close()
    logging.info(content)
    return content			


def sendmail(receiver,content):
	mail.send_mail(sender="joemilu@gmail.com",
				  to=receiver,
				  subject=u"千股千评",
				  body=content)

	
class TaskHandler(webapp.RequestHandler):
	def post(self):
                client = self.request.get('client')
                stock_list = self.request.get('stocks').split()
                logging.info(client)
                logging.info(stock_list)
                #get content
                content = get_stock_advices(stock_list)
                if 0 != len(content):
		    sendmail(client,content)
                    logging.info(content)
		
app = webapp.WSGIApplication([('/_ah/queue/default', WorkerHandler)],
                                     debug=True)
if __name__ == '__main__':
    run_wsgi_app(app)

