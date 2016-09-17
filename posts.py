from google.appengine.ext import ndb
from google.appengine.api import images


def blog_key(name='default'):
    # Setting up the blog key for the database
    return ndb.Key('blogs', name)


class Post(ndb.Model):

    """Parent class for Post
    useful subclasses:
    by_id
    create
    update"""

    # Setup of all the values for the database entity of Post
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    featured_img = ndb.BlobProperty()
    last_modified = ndb.DateTimeProperty(auto_now=True)
    likes = ndb.IntegerProperty()

    @classmethod
    def by_id(cls, uid):
        """Post.by_id takes one parameter which is the id of the post
        Post.by_id(12345)
        """
        return Post.get_by_id(uid, parent=blog_key())

    @classmethod
    def create(cls, subject, content, featured_img, user_id):
        """Post.create takes four parameters which is
        the subject, content, featured image and the user_id of the author
        Post.create("subject", "content", "image uploaded", "12345")
        """
        # Create list to collet errors
        cls.error_msg = []
        # Set has_error to false
        cls.has_error = False

        if not subject:
            # If there is no subject set has_error to True
            # and add error message
            cls.has_error = True
            cls.error_msg.extend(["You need to have a subject"])

        if not content:
            # If there is no content set has_error to True
            # and add error message
            cls.has_error = True
            cls.error_msg.extend(["You need to have content"])

        if featured_img:
            # If featured_img is uploaded resize it to fit better
            featured_img = images.resize(featured_img, width=750)
        else:
            # Else set it to None.
            featured_img = None

        if not cls.has_error:
            # If there are no errors create a post by calling the parent class.
            cls.p = Post(parent=blog_key(), subject=subject,
                         content=content, user_id=user_id,
                         featured_img=featured_img)
            # Then put the post into the database
            cls.p.put()
            # return to the CreatePostPage class in pages.py
            return cls
        else:
            # If there are errors just return the cls with the error_msg
            # return to the CreatePostPage class in pages.py
            return cls

    @classmethod
    def update(cls, post_id, subject, content,
               featured_img, delete_featured_img):
        """Post.update takes five parameters which is
        the subject, content, featured image, the user_id of the author and delete_featured_image which is True/False
        Post.create("subject", "content", "image uploaded", "12345", True)
        """
        # Fetch the post that is to be updated
        cls.p = cls.by_id(post_id)

        cls.error_msg = []
        cls.has_error = False

        if not subject:
            cls.has_error = True
            cls.error_msg.extend(["You need to have a subject"])
        else:
            # If subject exist add it to the entity
            cls.p.subject = subject

        if not content:
            cls.has_error = True
            cls.error_msg.extend(["You need to have content"])
        else:
            # If content exist add it to the entity
            cls.p.content = content

        if delete_featured_img:
             # If delete_featured_img is True then set the featured_img to None
            cls.p.featured_img = None

        if featured_img:
            # If there is a new featured_img uploaded resize it and then add it
            # to the entity
            cls.p.featured_img = images.resize(featured_img, width=1000)

        if not cls.has_error:
            # If no errors has come up put the entity back into the ndb
            cls.p.put()
            # Return to the class EditPost in pages.py
            return cls
        else:
            # If there are errors pass it along in cls
            # Return to the class EditPost in pages.py
            return cls
        return
