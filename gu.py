# g1 - geiger counter support utilities - TAS
# In generic python3 so testable on other platforms

from array import array

class A:
    # model the canonical behavior, however inefficiently
    def __init__(self):
        self.s = [0]
        self.m = [0]
        self.h = [0]
        self.d = [0]
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





class Accumulator:
    def __init__(self):
        self.seconds_value = array('H', (0 for i in range(300)))
        self.minutes_value = array('L', (0 for i in range(300)))
        self.i_seconds = self.i_minutes = 300-1

    def log_value(self, v):
        i_s = self.i_seconds = (self.i_seconds + 1) % 300
        if i_s % 60 == 0:
            self.new_minute()
        self.seconds_value[i_s] = v

    def new_minute(self):
        i_m = self.i_minutes = (self.i_minutes + 1) % 300        
        i = (self.i_seconds - 60) % 300
        self.minutes_value[i_m] = sum(self.seconds_value[i:i+60])
            
    def last_n_seconds(self, n):
        i_s = self.i_seconds
        s_v = self.seconds_value
        for i in range(n):            
            yield s_v[(i_s+300-i)%300]
            
    def last_n_minutes(self, n):
        i_s = self.i_minutes
        m_v = self.minutes_value
        for i in range(n):            
            yield m_v[(i_s+300-i)%300]
            


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

