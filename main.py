import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blogpost(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty( required = True)
    created = db.DateTimeProperty(auto_now_add = True)



class Blog(Handler):
    def render_front(self, title="", blogpost = ""):
        blogposts = db.GqlQuery("SELECT * FROM Blogpost "
                                "ORDER BY created DESC LIMIT 5")

        self.render("front.html", title=title, blogpost=blogpost, blogposts=blogposts)

    def get(self):
        self.render_front()

class Newpost(Handler):
    def render_newpost(self, title="", blogpost = "", error=""):
        self.render("newpost.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            b = Blogpost(title = title, blogpost=blogpost)
            b.put()

            id = b.key().id()
            self.redirect("/blog/%s" % id)
        else:
            error = "Your post needs a title and post"
            self.render_newpost(title, blogpost, error)


class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        blogpost = Blogpost.get_by_id(int(id))

        if blogpost:
            t = jinja_env.get_template("singlepost.html")
            response = t.render(blogpost=blogpost)
        else:
            error = "There is no blogpost with that id"
            t = jinja_env.get_template("error.html")
            response = t.render(error=error)

        self.response.out.write(response)


app = webapp2.WSGIApplication([
    ('/blog', Blog),
    ('/newpost', Newpost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
