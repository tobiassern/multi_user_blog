from google.appengine.ext import ndb


def comment_key(name='default'):
    # Setting up the comment key for the database
    return ndb.Key('comments', name)


class Comment(ndb.Model):

    """Parent class for Comment
    useful subclasses:
    by_id
    by_post_id
    create"""

    # Setup of all the values for the database entity of Post
    content = ndb.TextProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)
    post_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, comment_id):
        """Comment.by_id takes one parameter which is the id of the comment
        Comment.by_id(12345)
        """
        return Comment.get_by_id(int(comment_id), parent=comment_key())

    @classmethod
    def by_post_id(cls, post_id):
        """Comment.by_post_id takes one parameter which is the id of the post
        This is used to fetch all commments that belongs to one single post
        Comment.by_post_id(12345)
        """
        comments = Comment.query()
        comments = comments.filter(Comment.post_id == post_id)
        comments = comments.order(-Comment.created)
        comments = comments.fetch()
        return comments

    @classmethod
    def create(cls, content, post_id, user_id):
        """Comment.create takes three parameters which is
        the content, post_id (the post that the comment belongs to) and user_id (the author of the comment)
        Comment.create("content", post_id, user_id)
        """

        # Create list to collet errors
        cls.error_msg = []
        # Set has_error to false
        cls.has_error = False

        if not content:
            # If there is no content set has_error to True
            # and add error message
            cls.has_error = True
            cls.error_msg.extend(["You need to write a comment"])
        if content and len(content) < 5:
            # If there is content but it is shorter than 5 characters set has_error to True
            # and add error message
            cls.has_error = True
            cls.error_msg.extend(
                ["Your comment need to be more than 5 characters"])

        if not cls.has_error:
            # If there are no errors, create a new comment by calling the
            # parent class Comment
            cls.comment = Comment(parent=comment_key(),
                                  content=content, user_id=int(user_id),
                                  post_id=int(post_id))
            # Put the comment into the database
            cls.comment.put()
            # Return to the CommentPost class in pages.py
            return cls
        else:
            # If there are error return the cls with error_msg to the
            # CommentPost class in pages.py
            return cls
