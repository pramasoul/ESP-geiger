import cherrypy

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!\n"

cherrypy.quickstart(HelloWorld())
