#!/usr/env python
# -*- coding: utf-8 -*-
from HTMLParser import HTMLParser
import requests

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
    def handle_data(self, data):
    #        print "Data     :", data  
        if self.Found:
            self.recom = data
#            print "Data     :", data
            self.Found = False

SMTPserver = 'smtp.163.com'
sender =     'jokemilk@163.com'
destination = ['jokemilk@126.com']
USERNAME = "jokemilk"
PASSWORD = "420342034203"
# typical values for text_subtype are plain, html, xml
text_subtype = 'text'

subject=u"千股千评"
import sys

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText
def sendmail(content):
    try:
        msg = MIMEText(content, text_subtype,_charset='gbk')
        msg['Subject']= subject
        msg['From']   = sender # some SMTP servers will do this automatically, not all
        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False)
        conn.login(USERNAME, PASSWORD)
        try:
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            conn.close()
    except Exception, exc:
        sys.exit( "mail failed; %s" % str(exc) ) # give a error message


if __name__ == '__main__':
    content=''
    content.decode('gbk')
    for s in stocks:
        url = mock + s[0]
        P = MyParser()
        P.feed(requests.get(url).content.decode('gbk'))
        recon = P.recom
        content += s[1] + u': ' + recon + '\n\r'
        P.close()
    print content
    sendmail(content)