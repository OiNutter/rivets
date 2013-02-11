import sys
sys.path.insert(0,'../')
import cherrypy
import rivets
import os

class RivetsServer:
    """ Sample request handler class. """

    FIXTURE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),'fixtures'))

    @staticmethod
    def fixture_path(path):
        if path ==RivetsServer.FIXTURE_ROOT:
            return path
        else:
            return os.path.join(RivetsServer.FIXTURE_ROOT,path)

    def index(self):
        # CherryPy will call this method for the root URI ("/") and send
        # its return value to the client. Because this is tutorial
        # lesson number 01, we'll just send something really simple.
        # How about...
        return "HELLO WORLD"

    # Expose the index method through the web. CherryPy will never
    # publish methods that don't have the exposed attribute set to True
    index.exposed = True

import os.path
testconf = os.path.join(os.path.dirname(__file__), 'test.conf')

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().

    env = rivets.Environment()
    env.append_path(RivetsServer.fixture_path("server/app/javascripts"))
    env.append_path(RivetsServer.fixture_path("server/vendor/javascripts"))
    env.append_path(RivetsServer.fixture_path("server/vendor/stylesheets"))  

    d = cherrypy.dispatch.RoutesDispatcher()

    d.connect('assets','/assets/:path',controller = env, action='run')
    #d.connect('cached','/cached/javascripts',controller = env.index, action='run')
    d.connect('server','/',controller=RivetsServer(),action='index')

    conf = {
            '/':{
                'request.dispatch':d
            }
        }

    app = cherrypy.tree.mount(root=None,config=conf)
    cherrypy.quickstart(app)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(RivetsServer(), config=testconf)
