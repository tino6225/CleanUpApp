
from google.appengine.ext import ndb


class Location(ndb.Model):
    coordinates = ndb.StringProperty(required=True)
    comments = ndb.StringProperty(required=True)
    zipCode = ndb.StringProperty(required=True)


class Photo(ndb.Model):
    image = ndb.BlobProperty(required=True)
    mimetype = ndb.StringProperty()


class UserAccount(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
