# web server - TAS
import socket

class WS:
    def __init__(self):
        self.header = b"""HTTP/1.0 200 OK
Content-Type: text/html; charset=UTF-8
Content-Encoding: UTF-8
Content-Length: %d
Connection: close

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
        overhead = len(self.prefix) + len(self.suffix)
        addr = self.addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
        try:
            s = self.s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(addr)
            s.listen(2)
            print('listening on', addr)

            while True:
                try:
                    cl, ca = s.accept()
                    self.count += 1
                    message = b'%d\n' % self.count
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
                    cl_file.write(self.header % (len(message) + overhead))
                    cl_file.write(self.prefix)
                    cl_file.write(message)
                    cl_file.write(self.suffix)
                except:
                    raise
                finally:
                    cl_file.close()
                    cl.close()
        except:
            raise
        finally:
            s.close()

    def stop(self):
        self.s.close()

ws = WS()
ws.start()
