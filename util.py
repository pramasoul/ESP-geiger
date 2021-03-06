# random utilities - TAS
import os
import socket
from shutil import copyfileobj


def cat(path):
    with open(path) as f:
        for line in f:
            print(line, end='')


def df(path='/'):
    _ = os.statvfs('/')
    return _[1] * _[4]

def ifconfig():
    import network
    w = network.WLAN()
    return w.ifconfig()

def http_open(url):
    _, _, host, path = url.split('/', 3)
    if ':' in host:
        host, _ = host.split(':')
        port = int(_)
    else:
        port = 80
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    return s

def curlO(url):
    _, fname = url.rsplit('/',1)
    with open(fname, 'wb') as f:
        s = http_open(url)
        while s.readline() != b'\r\n':
            pass
        copyfileobj(s, f)

def pinServe():
    import machine
    pins = [machine.Pin(i, machine.Pin.IN) for i in (0, 2, 4, 5, 12, 13, 14, 15)]

    html = """<!DOCTYPE html>
    <html>
        <head> <title>ESP8266 Pins</title> </head>
        <body> <h1>ESP8266 Pins</h1>
            <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
        </body>
    </html>
    """

    import socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('listening on', addr)

    while True:
        cl, addr = s.accept()
        print('client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break
        rows = ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pins]
        response = html % '\n'.join(rows)
        cl.send(response)
        cl.close()
