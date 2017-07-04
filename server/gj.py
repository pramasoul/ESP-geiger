# Server-side receive, journal and decode
# -*- coding: utf-8 -*-
import gzip
from struct import calcsize, unpack_from

# Decode a Reporter packet
# Not part of a Reporting object, to keep it from weighing down the sensor module
# Has to understand the report() method of the client
def decodeReport(pkt):
    rv = dict()
    bi = 0
    rv['version'], rv['uid'] = unpack_from('!B4s', pkt, bi)
    bi += calcsize('!B4s')
    rv['sent_ts'], rv['cnt'] = unpack_from('!II', pkt, bi)
    bi += calcsize('!II')
    for strip_letter in 'smhd':
        n, code = unpack_from('!H2s', pkt, bi)
        #print(n, code)
        bi += calcsize('!H2s')
        dbi = calcsize(code)
        rv[strip_letter + '_counts'] = [unpack_from(code, pkt, bi + i*dbi)[0] for i in range(n)]
        bi += n * dbi
    #print(len(pkt) - bi, " bytes left: ", pkt[bi:])
    n_bssids = unpack_from('!B', pkt, bi)[0]
    l_uchar = calcsize('!B')
    bi += l_uchar
    rv['bssids'] = [(unpack_from('!B', pkt, bi + i * (l_uchar + 6))[0] - 200,
                     unpack_from('!6s', pkt, bi + i * (l_uchar + 6) + 1)[0])
                    for i in range(n_bssids)]
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

# OBSOLETE
def journal(f=None):
    l = UDPListener()
    for p in l:
        ts, addr, data = p
        if f:
            f.write(('%f %s %d %d\n' % (ts, addr[0], addr[1], len(data))).encode('UTF8'))
            f.write(data)
            f.write(b'\n')
        print(decodeReport(data))

# Temporary for testing
def j2(filename):
    l = UDPListener()
    j = Journal(filename)
    for p in l:
        j.record(p)
        print(decodeReport(p[-1]))


class Journal:
    def __init__(self, fname):
        self.fname = fname
        # FIXME: be smarter about determining if gzip-compressed
        self.gzit = fname.endswith('gz')
        if self.gzit:
            self.opener = gzip.open
        else:
            self.opener = open
        self.read_f = self.opener(fname, 'rb')

    def open_for_appending(self):
        self.write_f = self.opener(self.fname, 'ab')

    def record(self, p):
        ts, addr, data = p
        f = self.write_f
        f.write(('%f %s %d %d\n' % (ts, addr[0], addr[1], len(data))).encode('UTF8'))
        f.write(data)
        f.write(b'\n')

    def flush(self):
        self.write_f.flush()

    def close(self):
        self.flush()
        self.write_f.close()

    def __iter__(self):
        self.read_f.seek(0)
        return self

    def __next__(self):
        f = self.read_f
        hs = f.readline()
        if hs == b'\n':
            hs = f.readline()
        if hs == b'' or hs[-1] != ord(b'\n'):
            raise StopIteration
        h = hs.split()
        ts = float(h[0])
        addr = h[1].decode('UTF8'), int(h[2])
        len_data = int(h[3])
        data = f.read(len_data)
        if len(data) != len_data:
            raise StopIteration
        return ts, addr, data
