from google.appengine.ext import ndb
from models.posts import Post, blog_key

def likes_key(name='default'):
    # Setting up the comment key for the database
    return ndb.Key('likes', name)


class Likes(ndb.Model):

    """Parent class for Comment
    useful subclasses:
    by_id
    by_post_id
    create"""

    # Setup of all the values for the database entity of Post
    user_id = ndb.IntegerProperty(required=True)
    post_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def add_like(cls, post_id, user_id):
        """Comment.create takes three parameters which is
        the content, post_id (the post that the comment belongs to)
         and user_id (the author of the comment)
        Comment.create("content", post_id, user_id)
        """
       	like = Likes.query()
        like = like.filter(Likes.post_id == post_id and Likes.user_id == user_id)
        like = like.get()
        post = ndb.Key('Post', int(post_id), parent=blog_key())
        post = post.get()
        if not post.likes:
        	post.likes = 0
        cls.response = dict()
        if like:
        	like.key.delete()
        	post.likes = post.likes - 1
        	if post.likes < 0:
        		post.likes = 0
        	cls.response['type'] = 'not-liked'
        	cls.response['count'] = post.likes
        	cls.response['action'] = True
        else:
        	like = Likes(parent=likes_key(), post_id=post_id, user_id=user_id)
        	like.put()
        	post.likes = post.likes + 1
        	cls.response['type'] = 'liked'
        	cls.response['count'] = post.likes
        	cls.response['action'] = True
        post.put()
        return cls
