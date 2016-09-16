from google.appengine.ext import ndb


def comment_key(name='default'):
    return ndb.Key('comments', name)


class Comment(ndb.Model):
    content = ndb.TextProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)
    post_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, comment_id):
        return Comment.get_by_id(int(comment_id), parent=comment_key())

    @classmethod
    def by_post_id(cls, post_id):
        comments = Comment.query()
        comments = comments.filter(Comment.post_id == post_id)
        comments = comments.order(-Comment.created)
        comments = comments.fetch()
        return comments

    @classmethod
    def create(cls, content, post_id, user_id):
        cls.error_msg = []
        cls.has_error = False

        if not content:
            cls.has_error = True
            cls.error_msg.extend(["You need to write a comment"])
        if content and len(content) < 5:
            cls.has_error = True
            cls.error_msg.extend(
                ["Your comment need to be more than 5 characters"])

        if not cls.has_error:
            cls.comment = Comment(parent=comment_key(),
                                  content=content, user_id=int(user_id),
                                  post_id=int(post_id))
            cls.comment.put()
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
