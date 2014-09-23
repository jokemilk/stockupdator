from google.appengine.ext import ndb

class stockbooker(ndb.Model):
    mailaddr = ndb.StringProperty()
    stocklist = ndb.TextProperty()
