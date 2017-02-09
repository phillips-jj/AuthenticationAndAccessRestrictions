import cherrypy
import random
import string   

from auth import AuthController, require, member_of, name_is

# Customized version of the AuthenticationAndAccessRestrictions sample from http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions.
# I've added some Ajax/Javascript/REST calls based on the CherryPy tutorial, and also slightly enhanced some of the sample web pages.  Check out
# my WebAutomationCSharp sample to see how we can use NHTML to automate testing of this web UI.

class RestrictedArea:
    
    # all methods in this controller (and subcontrollers) is
    # open only to members of the admin group
    
    _cp_config = {
        'auth.require': [member_of('admin')]
    }
    
    @cherrypy.expose
    def index(self):
        return """This is the admin only area."""


class Root:
    
    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }
    
    auth = AuthController()
    
    restricted = RestrictedArea()
    
    def generatelogoutbutton(self):
        return """<form method="post" action="/auth/logout"><input type="submit" value="log out" />"""
    
    @cherrypy.expose
    @require()
    def generate(self):
        return open("generate.html")
    
    @cherrypy.expose
    @require()
    def index(self):
        s = "<html><body>This page only requires a valid login.  You are logged in as: " + cherrypy.request.login
        s += self.generatelogoutbutton()
        s += "<br><br>"
        s += "<a href=/auth/logout>Logout</a><br>"
        
        if cherrypy.request.login == 'joe':
            s += "<a href=/only_for_joe>Only For Joe</a><br>"
            if member_of("admin"):
                s += "<a href=/only_for_joe_admin>Only For Joe Admin</a><br>"

        s += "<a href=/generate>Generate Random String</a><br>"
        s += "<a href=/open>Open page</a><br>"
        s += "</body></html>"
        return s
    
    @cherrypy.expose
    def open(self):
        s = "This page is open to everyone. "
        return s
    
    @cherrypy.expose
    @require(name_is("joe"))
    def only_for_joe(self):
        return """Hello Joe - this page is available to you only"""

    # This is only available if the user name is joe _and_ he's in group admin
    @cherrypy.expose
    @require(name_is("joe"))
    @require(member_of("admin"))   # equivalent: @require(name_is("joe"), member_of("admin"))
    def only_for_joe_admin(self):
        return """Hello Joe Admin - this page is available to you only"""

@cherrypy.expose
class StringGeneratorWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return cherrypy.session['mystring']

    def POST(self, length=8):
        some_string = ''.join(random.sample(string.hexdigits, int(length)))
        cherrypy.session['mystring'] = some_string
        return some_string

    def PUT(self, another_string):
        cherrypy.session['mystring'] = another_string

    def DELETE(self):
        cherrypy.session.pop('mystring', None)

if __name__ == '__main__':
    conf = {
            '/generator': {
                           'request.dispatch': cherrypy.dispatch.MethodDispatcher()
                           }
            }
    
    webapp = Root()
    webapp.generator = StringGeneratorWebService()
    cherrypy.quickstart(webapp, '/', conf)