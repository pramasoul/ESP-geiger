import cherrypy
import hashlib
import json
from binascii import hexlify

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!\n"

    @cherrypy.expose
    def foo(self):
        return "bar\n"


def hashit(*args):
    m = hashlib.sha256()
    for v in args:
        if isinstance(v, str):
            v = v.encode('UTF8')
        m.update(v)
    return m.digest()


class Beetle:
    def __init__(self, ident=None, ss_hint=None, revision=None):
        self.id = ident
        with open(cherrypy.request.app.config['secrets']['secret_generating_secret_filename']) as f:
            sgs = json.load(f)['secret']
        self.shared_secret = hashit(sgs, ident, ss_hint)
        self.rev = revision

    def sign(self, value):
        return hexlify(hashit(self.shared_secret, value))
        
    def update_files(self):
        # FIXME: make real
        # This would come out of a configuration management database
        for name in [b'foo', b'bar', b'blort']:
            yield name, hashlib.sha256(b'Contents of ' + name).hexdigest()


@cherrypy.popargs('beetle_id', 'ss_hint', 'revision')
class Update:
    @cherrypy.expose
    def index(self, beetle_id, ss_hint, revision):
        beetle = Beetle(beetle_id, ss_hint, revision)
        rv = b'\n'.join(\
            b'http://192.168.32.69:8080/src/' +  path \
                + b' ' + beetle.sign(contents_hash) \
                for path, contents_hash in beetle.update_files())
        rv += b'\n%s\n' % beetle.sign(rv)
        return rv

    @cherrypy.expose
    def at(self, beetle_id, revision):
        return "You %s need these files\nAnd how about these?\n" % beetle_id

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080,
                       })

#cherrypy.quickstart(HelloWorld())

cherrypy.tree.mount(HelloWorld(), '/')
cherrypy.tree.mount(Update(), '/up', 'update_server.conf')
cherrypy.engine.start()
cherrypy.engine.block()

