# g1 - geiger counter support utilities - TAS
# In generic python3 so testable on other platforms

from array import array

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


# Alternative approaches:
# Log-based:
# - store every value in uint16
# - second counts are actual counts
# - all others are log-encoded
# enc = lambda x: int(log(x+1)*scale+0.5)
# dec = lambda x: int(exp(x/scale)-0.5)
# scale = 2918 to fit:
# enc((1<<16)*60*60*24) gives 65530

# Lin-log:
# - actual counts below knee
# - offset log above knee
# - knee is enc(scale)


class Strip:
    def __init__(self, code, length, period):
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
    
