#!/usr/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,"requests")
import requests

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import logging
from HTMLParser import HTMLParser
mock="http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/qgqp/index.phtml?symbol=sh"
stocks  = [['600679',u'金山开发'],['600754',u'锦江股份'],['601766',u'中国南车'],['600192',u'长城电工'],['600435',u'中兵光电']]

class MyParser(HTMLParser):
    Found = False
    def handle_starttag(self, tag, attrs):
    #        print "Start tag:", tag
        for name,value in attrs:
    #        print "     attr:", attr
            if name == 'title' and value == u'点击查看该股历史千股千评':
                self.Found = True
                logging.info("Found")
    def handle_data(self, data):
    #        print "Data     :", data  
        if self.Found:
            self.recom = data
#            print "Data     :", data
            self.Found = False

def Get_command():			
    content=''
    content.decode('gbk')
    for s in stocks:
        url = mock + s[0]
        P = MyParser()
        P.feed(requests.get(url).content.decode('gbk'))
        recon = P.recom
        content += s[1] + u': ' + recon + u'\n\r'
        P.close()
	logging.info(content)
    return content			

from google.appengine.api import mail

def sendmail(con):
	mail.send_mail(sender="joemilu@gmail.com",
				  to="jokemilk@126.com",
				  subject=u"千股千评",
				  body=con)

	
class ParseXMLHandler(webapp.RequestHandler):
	def get(self):
		logging.warning("hello world")
		logging.warning(u"你好")
		con = Get_command()
		logging.info(con)
		sendmail(con)
		
app = webapp.WSGIApplication([('/stock_updater', ParseXMLHandler)],
                                     debug=True)
if __name__ == '__main__':
    run_wsgi_app(app)

