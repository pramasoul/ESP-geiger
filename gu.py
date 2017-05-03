# gu - geiger counter support utilities - TAS
# In generic python3 so testable on other platforms

from array import array
import socket
import time
from ustruct import calcsize, pack_into

# Objective:
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


# Alternative approaches, not implemented:
# Logarithm-based:
# - store every value in uint16
# - second counts are actual counts
# - all others are log-encoded
# enc = lambda x: int(log(x+1)*scale+0.5)
# dec = lambda x: int(exp(x/scale)-0.5)
# scale = 2918 to fit:
# enc((1<<16)*60*60*24) gives 65530
#
# Lin-log:
# - actual counts below knee
# - offset log above knee
# - knee is enc(scale)


# A Strip is a window of stored history. It has a limited length
# of stored history. It has a period, which is the number of its
# stored values which get summed to make up the next single value
# in the next-coarser-grained Strip in an Accumulator (FIXME: refactor).
# It has a code, the storage type of the elements in the array
# that contains the history.
class Strip:
    def __init__(self, code, length, period):
        self.code = code
        self.network_order_code = '!' + code # for noalloc pack_into(fmt)
        self.data = array(code, (0 for i in range(length)))
        self.period = period
        self.ix = 0
        self.count = 0
    
    def note(self, v):
        ix = self.ix = (self.ix + 1) % len(self.data)
        self.data[ix] = v
        self.count += 1
        return self.count % self.period == 0

    def last_n(self, n):
        ix = self.ix
        data = self.data
        capacity = len(data)
        for i in range(min(n, capacity, self.count)):
            yield data[(ix + capacity - i)%capacity]
        
    def period_sum(self):
        return sum(self.last_n(self.period))


# An Accumulator is given an integer value every second, and can
# provide the "last N" values for seconds, and binned values
# for last N minutes, hours, and days, up to one year.
class Accumulator:
    def __init__(self):
        self.s = Strip('H', 300, 60)
        self.m = Strip('L', 300, 60)
        self.h = Strip('L', 300, 24)
        self.d = Strip('L', 300, 365)

    def log_value(self, v):
        if self.s.note(v):
            if self.m.note(self.s.period_sum()):
                if self.h.note(self.m.period_sum()):
                    if self.d.note(self.h.period_sum()):
                        # a year's worth, FIXME
                        pass
                    
    def last_n_seconds(self, n):
        yield from self.s.last_n(n)

    def last_n_minutes(self, n):
        yield from self.m.last_n(n)
    
    def last_n_hours(self, n):
        yield from self.h.last_n(n)
    
    def last_n_days(self, n):
        yield from self.d.last_n(n)
    

# A Reporter reports some contents of an Accumulator log
# via packed binary UDP to a host
class Reporter:
    def __init__(self, g, host, log):
        self.g = g
        self.host = host
        self.log = log
        self.addr = socket.getaddrinfo(host, 27183)[0][-1]
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buf = bytearray(512)
        bv = self.bv = memoryview(self.buf)
        bv[0] = 1               # version
        bv[1:5] = g.uid
        self.bi = 5

    def send(self):
        def append(strip, n):
            # Append up to n values from the specified Strip, with header
            bi_for_header = bi
            fmt = strip.network_order_code
            assert len(fmt) == 2
            bi += calcsize('!H2s')
            di = calcsize(fmt)
            qty = 0
            for v in strip.last_n(n):
                pack_into(fmt, buf, bi, v)
                bi += di
                qty += 1
            pack_into('!H2s', buf, bi_for_header, qty, strip.network_order_code)

        buf = self.buf
        bi = self.bi
        bv = self.bv
        acc = self.log.acc

        pack_into('!II', buf, bi, time.time(), acc.s.count)
        bi += calcsize('!II')
        append(acc.s, 60)
        append(acc.m, 60)
        append(acc.h, 24)
        append(acc.d, 30)

        # Followed by the bssid's with signal strength
        if True:
            l_uchar = calcsize('!B')
            bslist = self.g.bssids
            pack_into('!B', buf, bi, len(bslist))
            bi += l_uchar
            for dbm, bssid in bslist:
                pack_into('!B', buf, bi, 200+dbm)
                bi += l_uchar
                bv[bi:bi+6] = bssid
                bi += 6

        r = self.s.sendto(bv[:bi], self.addr)
        self.bi = 5

def update_bssids(g):
    g.bssids = sorted(((v[3], v[1]) \
                       for v in g.wlan.scan()), reverse=True)
