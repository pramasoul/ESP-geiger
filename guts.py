# guts - geiger counter support utilities test support - TAS
# In generic python3 so testable on other platforms

# Test components intended to support this:
# Monitor the Geiger counter count every second
# Be able to provide:
# - count each second for the last 300 seconds
# - count each minute for the last 300 minutes
# - count each hour for the last 300 hours
# - count each day for the last 300 days (maybe)
#
# Assume max counting rate is < 2**16/sec
# Second-counts can be stored in uint16
# The rest should be uint32


import socket
import time
import zlib


class CanonicalAccumulator:
    # model the canonical behavior, however inefficiently
    # This allows us to test the unit test code
    def __init__(self):
        self.s = []
        self.m = []
        self.h = []
        self.d = []
        self.n_s = 0

    def log_value(self, v):
        self.s.insert(0,v)
        self.s = self.s[:300]
        self.n_s += 1
        if self.n_s % 60 == 0:
            self.m.insert(0,sum(self.s[:60]))
            self.m = self.m[:300]
        if self.n_s % (60*60) == 0:
            self.h.insert(0,sum(self.m[:60]))
            self.h = self.h[:300]
        if self.n_s % (60*60*24) == 0:
            self.d.insert(0,sum(self.h[:24]))
            self.d = self.d[:300]


    def _last_n(self, n, what):
        for i in range(min(n, len(what))):
            yield what[i]

    def last_n_seconds(self, n):
        return self._last_n(n, self.s)

    def last_n_minutes(self, n):
        return self._last_n(n, self.m)

    def last_n_hours(self, n):
        return self._last_n(n, self.h)

    def last_n_days(self, n):
        return self._last_n(n, self.d)

# micropython has the const() pseudo-function, which is in effect a compiler pragma
def const(v):
    return v

from struct import calcsize, unpack_from

# Decode a Reporter packet
def decodeReport(pkt):
    rv = dict()
    bi = 0
    rv['version'], rv['uid'] = unpack_from('!B4s', pkt, bi)
    bi += calcsize('!B4s')
    rv['sent_ts'], rv['cnt'] = unpack_from('!II', pkt, bi)
    bi += calcsize('!II')
    for strip_letter in 'smhd':
        n, code = unpack_from('!H2s', pkt, bi)
        print(n, code)
        bi += calcsize('!H2s')
        dbi = calcsize(code)
        rv[strip_letter + '_counts'] = [unpack_from(code, pkt, bi + i*dbi)[0] for i in range(n)]
        bi += n * dbi
    return rv


class UDPListener(object):
    def __init__(self, host='0.0.0.0', port=27183, **kwargs):
        if 'sock' in kwargs:
            self.sock = kwargs['sock']
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((host, port))

    def __iter__(self):
        return self

    def __next__(self):
        return self.next_triple()

    def next_triple(self):
        data, addr = self.sock.recvfrom(65536)
        ts = time.time()
        if data.startswith(b'x'):
            try:
                data = zlib.decompress(data)
            except zlib.error:
                pass
        return ts, addr, data

def pr():
    l = UDPListener()
    for p in l:
        print(decodeReport(p[-1]))
