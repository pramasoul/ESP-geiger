# web server - TAS
import pdb

import socket

class WS:
    def __init__(self):
        self.header = b"""HTTP/1.0 200 OK\r
Content-Type: text/html; charset=UTF-8\r
Content-Encoding: UTF-8\r
Content-Length: %d\r
Connection: close\r
\r
"""
        self.handlers = {}

    def start(self):
        addr = self.addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
        try:
            s = self.s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(addr)
            s.listen(2)
            print('listening on', addr)
        except:
            s.close()

    def handle_one(self, timeout=0.1):
        s = self.s
        s.settimeout(timeout)
        try:
            cl, ca = s.accept()
        except OSError:
            return 0
        print('client connected from', ca)
        #pdb.set_trace()
        cl_file = cl.makefile('rwb', 0)
        line = cl_file.readline().rstrip(b'\r\n')
        print(line)
        cmd, path, ver = line.split()
        while True:
            line = cl_file.readline()#.rstrip(b'\r\n')
            print(line)
            if not line or line == b'\r\n':
                break
        if cmd in self.handlers:
            resp = self.handlers[cmd](path)
        else:
            resp = b'Huh?'
        cl_file.write(self.header % len(resp))
        cl_file.write(resp)
        cl_file.close()
        cl.close()
        return len(resp)


    def stop(self):
        self.s.close()

class GET_handler:
    def __init__(self):
        self.prefix = b"""<!DOCTYPE html>
<html>
 <head>
  <title>Trivial Web Server</title>
  <link rel="icon" href="data:;base64,iVBORw0KGgo=">
 </head>
 <body>
  <h1>Test</h1>
"""
        self.suffix = b"""</body></html>"""
        self.count = 0

    def get(self, path):
        self.count += 1
        if path == b'/count':
            return self.prefix + str(self.count).encode('UTF8') + self.suffix
        return self.prefix + \
            b'<pre>%s</pre>' % path + self.suffix

ws = WS()
gh = GET_handler()
ws.handlers[b'GET'] = gh.get
ws.start()
while True:
    ws.handle_one(1)
ws.handle_one(10)
pdb.set_trace()
