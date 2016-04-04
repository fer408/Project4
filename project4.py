# codes that import os
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

# codes that import jinja 2 and webapp
import jinja2
import webapp2

# code that imports database
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                 autoescape = True)

COMMENT_WALL ="Public"
DEFAULT_ERROR = " Error Enter a valid comment"

def wall_key(wall_name=COMMENT_WALL):

  return ndb.Key('Wall', wall_name)

class Author(ndb.Model):
  """Sub model for representing an author."""
  identity = ndb.StringProperty(indexed=True)
  name = ndb.StringProperty(indexed=False)
  email = ndb.StringProperty(indexed=False)

class Post(ndb.Model):
  """A main model for representing an individual post entry."""
  author = ndb.StructuredProperty(Author)
  content = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)

#code of the class that will be inherited by the other classes.

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **kw):
    t = jinja_env.get_template(template)
    return t.render(**kw)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))
# code to handle my MenuPage
class MenuPage(webapp2.RequestHandler):
  def get(self):
    wall_name = self.request.get('wall_name',COMMENT_WALL)
    if wall_name == COMMENT_WALL.lower(): wall_name = COMMENT_WALL
    error  = self.request.get("error")


    # [START query]
    posts_query = Post.query(ancestor = wall_key(wall_name)).order(-Post.date)

    # The function fetch() returns all posts that satisfy our query. The function returns a list of
    # post objects
    posts =  posts_query.fetch()
    # [END query]

    # If a person is logged into Google's Services
    user = users.get_current_user()
    if user:
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        user_name = user.nickname()
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        user_name = 'Anonymous Poster'


    template_values = {
      "user": user,
      "error": error,
      "wall_name": urllib.quote_plus(wall_name),
      "posts": posts,
      "url": url,
      "url_linktext":url_linktext
        }

    template1 = jinja_env.get_template('comment_wall.html')
    self.response.write(template1.render(template_values))


class CommentWall(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Post' to ensure each
    # Post is in the same entity group. Queries across the
    # single entity group will be consistent. However, the write
    # rate to a single entity group should be limited to
    # ~1/second.
    wall_name = self.request.get('wall_name',COMMENT_WALL)
    post = Post(parent=wall_key(wall_name))

    # When the person is making the post, check to see whether the person
    # is logged into Google
    if users.get_current_user():
      post.author = Author(
            identity=users.get_current_user().user_id(),
            name=users.get_current_user().nickname(),
            email=users.get_current_user().email())
    else:
      post.author = Author(
            name='anonymous@anonymous.com',
            email='anonymous@anonymous.com')


    # Get the content from our request parameters, in this case, the message
    # is in the parameter 'content'
    post.content = self.request.get('content')
    if post.content == '':
      self.redirect('/?wall_name=' + wall_name + '&error=' + DEFAULT_ERROR)
    else:
    # Write to the Google Database
      post.put()

    # Do other things here such as a page redirect
      self.redirect("/?wall_name=" + wall_name)

class Lesson1(Handler):
  def get(self):

    self.render("project4html1.html")
# code that handles my lesson 2 html page
class Lesson2(Handler):
  def get(self):

    self.render("project4html2.html")
# code that handles my lesson 3 html page
class Lesson3(Handler):
    def get(self):
      self.render("project4html3.html")
#code that handles my lesson 4 html page
class Lesson4(Handler):
    def get(self):
      self.render("project4html4.html")



app = webapp2.WSGIApplication([("/", MenuPage),
                             ("/sign", CommentWall),
                             ("/project4html1",Lesson1),
                             ("/project4html2",Lesson2),
                             ("/project4html3",Lesson3),
                             ("/project4html4",Lesson4)], debug=True)
