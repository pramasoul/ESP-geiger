# web server - TAS
import socket
from sys import stderr

from uwsgi import run_wsgi

def b2s(b):
    return b.decode('iso-8859-1')

class WS:
    def __init__(self, app):
        self.header = b"""HTTP/1.0 200 OK\r
Content-Type: text/html; charset=UTF-8\r
Content-Encoding: UTF-8\r
Content-Length: %d\r
Connection: close\r
\r
"""
        self.app = app
        self.err = stderr
        self.verbose = True
        

    def start(self):
        addr = self.addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
        try:
            s = self.s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(addr)
            s.listen(2)
            self.verbose and print('listening on', addr)
        except:
            s.close()

    def handle_one(self, timeout=0.1):
        s = self.s
        s.settimeout(timeout)
        try:
            cl, ca = s.accept()
        except OSError:
            return 0
        self.verbose and print('client connected from', ca)
        cl_file = cl.makefile('rwb', None)
        line = b2s(cl_file.readline()).rstrip('\r\n')
        self.verbose and print(line)

        env = { 'wsgi.errors': self.err }
        cmd, path, ver = line.split()
        env['REQUEST_METHOD'] = cmd
        qix = path.find('?')
        if qix == -1:
            env['PATH_INFO'] = path
        else:
            env['PATH_INFO'] = path[:qix]
            env['QUERY_STRING'] = path[qix+1:]

        while True:
            # With more resources we would collect these headers into env
            # Here we just discard them
            line = cl_file.readline()#.rstrip(b'\r\n')
            self.verbose and print(line)
            if not line or line == b'\r\n':
                break

        run_wsgi(self.app, env, cl_file)
        cl.close()


    def stop(self):
        self.s.close()
