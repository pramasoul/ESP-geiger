# web server - TAS
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

    def serveOne(self, timeout=0.1):
        s = self.s
        s.settimeout(timeout)
        self.count += 1
        message = b'%d\n' % self.count
        n_bytes = len(self.prefix) \
                  + len(self.suffix) \
                  + len(message)
        try:
            cl, ca = s.accept()
        except OSError:
            n_bytes = 0
        else:
            print('client connected from', ca)
            cl_file = cl.makefile('rwb', 0)
            while True:
                line = cl_file.readline()
                print(line)
                if not line or line == b'\r\n':
                    break
            #cl.send(self.prefix)
            #cl.send(str(self.count).encode('UTF8'))
            #cl.send(self.suffix)
            cl_file.write(self.header % n_bytes)
            cl_file.write(self.prefix)
            cl_file.write(message)
            cl_file.write(self.suffix)
            cl_file.close()
            cl.close()
        finally:
            return n_bytes


    def stop(self):
        self.s.close()

ws = WS()
ws.start()
import pdb
pdb.set_trace()
