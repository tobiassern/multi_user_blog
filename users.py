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
    # Making a secure value for password
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    # Used to check a secure value for password
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


def make_salt(length=5):
    # Creating a salt for make_pw_hash
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    # Creating a pw_hash to store password in database
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    # Check and set valid password
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group='default'):
    # Setting up the users key for the database
    return ndb.Key('users', group)


class User(ndb.Model):

    """Parent class for Users
    useful subclasses:
    by_id
    username_by_id
    by_name
    register
    update
    login
    """

    # Setup of all the values for the database entity of User
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    profile_img = ndb.BlobProperty()
    description = ndb.TextProperty()

    @classmethod
    def by_id(cls, uid):
        """User.by_id takes one parameter which is the id of the user
        User.by_id(12345)
        """
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def username_by_id(cls, uid):
        """User.username_by_id takes one parameter which is the id of the user
        Returns the username only. Using this for the comments
        User.username_by_id(12345)
        """
        u = User.get_by_id(uid, parent=users_key())
        return u.name

    @classmethod
    def by_name(cls, name):
        """User.by_name takes one parameter which is the name of the user
        User.by_name(name)
        """
        u = User.query()
        u = u.filter(User.name == name)
        u = u.get()
        return u

    @classmethod
    def register(cls, name, pw, email=None,
                 description=None, profile_img=None):
        """User.register takes five parameter which is
        the name (req), password (req), email, description and profile image
        User.register(name, pw, email, description, profile_img)
        """

        if profile_img:
            # If the profile image is set resize it
            profile_img = images.resize(profile_img, width=400)
        else:
            # Else set it to None
            profile_img = None

        # Hashing the password to store it securely in the database
        pw_hash = make_pw_hash(name, pw)

        # Return and register the User by calling the parent User class on
        # return
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email,
                    description=description,
                    profile_img=profile_img)

    @classmethod
    def update(cls, name, pw, email, description,
               profile_img, delete_profile_img, user_id):
        """User.update takes six parameter which is
        the name (req), password (req), email, description, profile image
        and delete_profile_img which is True/False
        User.update(name, pw, email, description, profile_img, delete_profile_img)
        """

        # Fetch the user to update
        user = User.by_id(int(user_id))

        # Update the username
        user.name = name
        # Update the email
        user.email = email
        # Update the description
        user.description = description

        if pw:
            # If a new password is entered hash it and store it
            pw_hash = make_pw_hash(name, pw)
            user.pw_hash = pw_hash

        if delete_profile_img:
            # If delete_profile_img is True then remove the profile_img
            user.profile_img = None

        if profile_img:
            # If a new profile img is added resize it and store it.
            profile_img = images.resize(profile_img, width=400)
            user.profile_img = profile_img

        # Put everything back into the database
        user.put()
        return

    @classmethod
    def login(cls, name, pw):
        """User.login takes two parameter which is the username and password
        User.login(name, pw)
        """
        # First check if the username exists
        u = cls.by_name(name)
        # If it exists and the password is valid return the user to LoginPage
        # class in pages.py
        if u and valid_pw(name, pw, u.pw_hash):
            return u
