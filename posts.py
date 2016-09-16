from google.appengine.ext import ndb

from google.appengine.api import images


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    featured_img = ndb.BlobProperty()
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, uid):
        return Post.get_by_id(uid, parent=blog_key())

    @classmethod
    def create(cls, subject, content, featured_img, user_id):

        cls.error_msg = []
        cls.has_error = False

        if not subject:
            cls.has_error = True
            cls.error_msg.extend(["You need to have a subject"])

        if not content:
            cls.has_error = True
            cls.error_msg.extend(["You need to have content"])

        if featured_img:
            featured_img = images.resize(featured_img, width=750)
        else:
            featured_img = None

        if not cls.has_error:
            cls.p = Post(parent=blog_key(), subject=subject,
                         content=content, user_id=user_id,
                         featured_img=featured_img)
            cls.p.put()
            return cls
        else:
            return cls

    @classmethod
    def update(cls, post_id, subject, content,
               featured_img, delete_featured_img):
        cls.p = cls.by_id(post_id)

        cls.error_msg = []
        cls.has_error = False

        if not subject:
            cls.has_error = True
            cls.error_msg.extend(["You need to have a subject"])
        else:
            cls.p.subject = subject

        if not content:
            cls.has_error = True
            cls.error_msg.extend(["You need to have content"])
        else:
            cls.p.content = content

        if delete_featured_img:
            cls.p.featured_img = None

        if featured_img:
            cls.p.featured_img = images.resize(featured_img, width=1000)

        if not cls.has_error:
            cls.p.put()
            return cls
        else:
            return cls
        return
