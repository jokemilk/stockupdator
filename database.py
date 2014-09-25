from google.appengine.ext import ndb

class client_db(ndb.Model):
    mail = ndb.StringProperty(required=True)
    stocklist = ndb.TextProperty()
