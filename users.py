# Split up the user functionality in separate file to make the code easier
# to read
from google.appengine.api import images
from google.appengine.ext import ndb
import hashlib
import hmac
import random
from string import letters

secret = '18vhJmuJNd'


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group='default'):
    return ndb.Key('users', group)


class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    profile_img = ndb.BlobProperty()
    description = ndb.TextProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def username_by_id(cls, uid):
        u = User.get_by_id(uid, parent=users_key())
        return u.name

    @classmethod
    def by_name(cls, name):
        u = User.query()
        u = u.filter(User.name == name)
        u = u.fetch()
        return u

    @classmethod
    def register(cls, name, pw, email=None,
                 description=None, profile_img=None):

        if profile_img:
            profile_img = images.resize(profile_img, width=400)
        else:
            profile_img = None

        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email,
                    description=description,
                    profile_img=profile_img)

    @classmethod
    def update(cls, name, pw, email, description, profile_img, delete_profile_img, user_id):

        user = User.by_id(int(user_id))
        user.name = name
        user.email = email
        user.description = description

        if pw:
            pw_hash = make_pw_hash(name, pw)
            user.pw_hash = pw_hash

        if delete_profile_img:
            user.profile_img = None
        if profile_img:
            profile_img = images.resize(profile_img, width=400)
            user.profile_img = profile_img

        user.put()
        return

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
