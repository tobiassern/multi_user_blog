# Split up the pages functionality in separate file to make the code
# easier to read

import os
import re
import webapp2
import jinja2
from google.appengine.ext import ndb

from google.appengine.api import images

# Importing local .py files
from users import User, users_key, make_secure_val, check_secure_val
from posts import Post, blog_key
from comments import Comment, comment_key

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class MainPage(Handler):

    def get(self):
        posts = Post.query()
        posts = posts.order(-Post.created)
        posts = posts.fetch()
        self.render('index.html', posts=posts)


# User Pages

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class RegisterPage(Handler):
    def get(self):
        if self.user:
            self.redirect("/profile/" + self.user.name)
        else:
            self.render("register.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        self.description = self.request.get('description')
        self.profile_img = self.request.get('profile_img')
        self.error_msg = []
        self.params = dict(username = self.username,
                      email = self.email, description = self.description)

        if not valid_username(self.username):
            self.error_msg.extend(["That's not a valid username."])
            have_error = True

        if not valid_password(self.password):
            self.error_msg.extend(["That wasn't a valid password."])
            have_error = True
        elif self.password != self.verify:
            self.error_msg.extend(["Your passwords didn't match."])
            have_error = True

        if not valid_email(self.email):
            self.serror_msg.extend(["That's not a valid email."])
            have_error = True

        if have_error:
            self.params['error_msg'] = self.error_msg
            self.render('register.html', **self.params)
        else:
            self.done()

    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            self.error_msg.extend(["That user already exists."])
            self.params['error_msg'] = self.error_msg
            self.render('register.html', **self.params)
        else:
            u = User.register(self.username, self.password, self.email, self.description, self.profile_img)
            u.put()

            self.login(u)
            self.redirect('/profile/' + u.name)

class EditProfilePage(Handler):
    def get(self):
        if self.user:
            user = User.by_id(int(self.user.key.id()))
            self.render("edit-profile.html", user=user)
        else:
            self.redirect("/login")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        self.description = self.request.get('description')
        self.profile_img = self.request.get('profile_img')
        self.delete_profile_img = self.request.get('delete_profile_img')
        self.user_id = self.user.key.id()
        self.error_msg = []
        self.params = dict(username = self.username,
                      email = self.email, description = self.description)

        if not valid_username(self.username):
            self.error_msg.extend(["That's not a valid username."])
            have_error = True
        if self.password:
            if not valid_password(self.password):
                self.error_msg.extend(["That wasn't a valid password."])
                have_error = True
            elif self.password != self.verify:
                self.error_msg.extend(["Your passwords didn't match."])
                have_error = True

        if not valid_email(self.email):
            self.serror_msg.extend(["That's not a valid email."])
            have_error = True

        if have_error:
            self.params['error_msg'] = self.error_msg
            self.render('register.html', **self.params)
        else:
            self.done()

    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u and not self.username == self.user.name:
            self.error_msg.extend(["That user already exists."])
            self.params['error_msg'] = self.error_msg
            self.render('register.html', **self.params)
        else:
            user_update = User.update(self.username, self.password, self.email, self.description, self.profile_img, self.delete_profile_img, self.user_id)
            self.redirect('/profile/' + self.user.name)

class LoginPage(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

# Blog Pages

class BlogPage(Handler):

    def get(self):
        self.redirect('/')


class PostPage(Handler):

    def get(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()

        if not post:
            self.response.set_status(404)
            self.render("404.html")
            return
        comments = Comment.by_post_id(int(post_id))
        comment_output = []
        for comment in comments:
            user_name = User.username_by_id(int(comment.user_id))
            if not user_name:
                user_name = "Deleted User"

            comment = dict(content=comment.content, created=comment.created,
                           user_name=user_name, comment_id=comment.key.id())
            comment_output.append(comment)

        author = User.by_id(post.user_id)
        self.render(
            "post.html", post=post, author=author,
            comment_output=comment_output)


class CreatePostPage(Handler):

    def get(self):
        if self.user:
            self.render('create-post.html')
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/')

        subject = self.request.get('subject')
        content = self.request.get('content')
        user_id = self.user.key.id()
        featured_img = self.request.get('featured_img')

        post = Post.create(subject, content, featured_img, user_id)
        if post.has_error:
            params = dict(
                subject=subject, content=content, error_msg=post.error_msg)
            self.render('create-post.html', **params)
        else:
            self.redirect('/blog/%s' % str(post.p.key.id()))


class EditPost(Handler):

    def get(self, post_id):
        post = Post.by_id(int(post_id))

        if not self.user:
            self.redirect('/blog/' + post_id)
            return
        if post.user_id == self.user.key.id():
            self.render("edit-post.html", post=post)
        else:
            self.redirect('/blog/' + post_id)

    def post(self, post_id):

        subject = self.request.get('subject')
        content = self.request.get('content')
        delete_featured_img = self.request.get('delete_featured_img')
        featured_img = self.request.get('featured_img')

        post = Post.update(
            int(post_id), subject, content, featured_img, delete_featured_img)
        if post.has_error:
            params = dict(
                subject=subject, content=content, error_msg=post.error_msg)
            self.render('edit-post.html', **params)
        else:
            self.redirect('/blog/%s' % str(post.p.key.id()))


class DeletePost(Handler):

    def get(self, post_id):
        post = Post.by_id(int(post_id))
        if not self.user:
            self.redirect('/blog/' + post_id)
            return

        if post.user_id == self.user.key.id():
            post.key.delete()
            self.redirect('/profile/' + self.user.name)
        else:
            self.redirect('/blog/' + post_id)


class DeleteComment(Handler):

    def get(self, comment_id, post_id):
        self.write(comment_id)
        comment = Comment.get_by_id(int(comment_id), parent=comment_key())
        if not comment:
            self.redirect('/blog/' + post_id + '#commentlist')
            return

        if not self.user:
            self.redirect('/blog/' + post_id + '#commentlist')
            return

        if comment.user_id == self.user.key.id():
            comment.key.delete()
            self.redirect('/blog/' + post_id + '#commentlist')
        else:
            self.redirect('/blog/' + post_id + '#commentlist')


class CommentPost(Handler):

    def post(self, post_id):
        content = self.request.get('comment')
        user_id = self.user.key.id()
        comment = Comment.create(content, post_id, user_id)
        if comment.has_error:
            self.write("error")
        else:
            self.redirect('/blog/%s#%s' % (str(post_id), "commentform"))


class MissingPage(Handler):

    def get(self):
        self.response.set_status(404)
        self.render("404.html")
        return


class Logout(Handler):

    def get(self):
        self.logout()  # Call logout function of parent class Handler
        self.redirect('/')  # Redirect to frontpage on logout


class RouteProfile(Handler):

    def get(self):
        self.redirect('/')


class ProfilePage(Handler):

    def get(self, user_profile):
        current_user_profile = User.by_name(user_profile)
        current_user_profile = current_user_profile[0]
        if not current_user_profile:
            self.response.set_status(404)
            self.render("404.html")
            return
        posts = Post.query()
        posts = posts.filter(Post.user_id == current_user_profile.key.id())
        posts = posts.order(-Post.created)
        posts = posts.fetch()

        self.render(
            'profile.html', user_profile=current_user_profile, posts=posts)


class Image(Handler):

    def get(self):
        img_id = self.request.get('id')
        img_type = self.request.get('type')
        if img_id.isdigit():
            if img_type == 'featured_img':
                img_key = ndb.Key('Post', int(img_id), parent=blog_key())
            elif img_type == "profile_img":
                img_key = ndb.Key('User', int(img_id), parent=users_key())

            if img_key:
                img = img_key.get()
                if img_type == "featured_img":
                    if img.featured_img:
                        self.response.headers['Content-Type'] = 'image/png'
                        self.response.out.write(img.featured_img)
                        return

                elif img_type == "profile_img":
                    if img.profile_img:
                        self.response.headers['Content-Type'] = 'image/png'
                        self.response.out.write(img.profile_img)
                        return

        self.response.set_status(404)
        self.render("404.html")


appLoader = webapp2.WSGIApplication([('/', MainPage),
                                     ('/register', RegisterPage),
                                     ('/login', LoginPage),
                                     ('/logout', Logout),
                                     ('/profile', RouteProfile),
                                     ('/profile/(\w+)', ProfilePage),
                                     ('/edit-profile', EditProfilePage),
                                     ('/create-post', CreatePostPage),
                                     ('/blog/([0-9]+)/edit', EditPost),
                                     ('/blog/([0-9]+)/delete', DeletePost),
                                     ('/comment/([0-9]+)', CommentPost),
                                     ('/comment/([0-9]+)/([0-9]+)/delete',
                                      DeleteComment),
                                     ('/blog', BlogPage),
                                     ('/blog/([0-9]+)', PostPage),
                                     ('/img', Image),
                                     ('/.*', MissingPage)
                                     ],
                                    debug=True)