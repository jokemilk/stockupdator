from google.appengine.ext import ndb

class client_db(ndb.Model):
    mail = ndb.StringProperty(required=True)
    stockcnt = ndb.IntegerProperty()
    stocklist = ndb.TextProperty()
