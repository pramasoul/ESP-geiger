# g1 - geiger counter -TAS

import micropython
micropython.alloc_emergency_exception_buf(100)
from machine import Pin, Timer, disable_irq, enable_irq, idle
from machine import unique_id

import socket
from ubinascii import b2a_base64
from gu import Accumulator, Reporter


class Geiger:
    def __init__(self):
        self.led = Pin(0, Pin.OUT, value=1)
        # FIXME: does pull-up work with Sparkfun Geiger tube?
        self.sense = Pin(14, Pin.IN, Pin.PULL_UP)
        # "noise" pin tells us to expect false pulses on sense,
        # so should ignore them for some time (a few ms)
        self.noise = Pin(12, Pin.IN, Pin.PULL_UP)
        self.scb = self.ncb = None
        self.ntim = Timer(-1)
        self.counter = 0

    def start(self):
        if self.scb:
            # Sparkfun geiger tube is ?rising-edge pulse
            # Radiation-watch PIN array sensor pulls low on signal but
            # rising-edge works and gives epsilon more time to respond to noise
            self.scb.trigger(self.sense.IRQ_RISING)
            return

        def scbf(pin):
            #was = disable_irq() # unnecessary as we are the only modifier
            self.counter += 1
            #enable_irq(was)
            self.bip()

        self.scb = self.sense.irq(handler=scbf,
                                 trigger=self.sense.IRQ_RISING)

        # Noise pin shall produce 5ms dead time
        def ncbf(pin):
            self.ntim.init(period=5, mode=Timer.ONE_SHOT,
                           callback=lambda t: self.scb.trigger(self.sense.IRQ_RISING))
            self.scb.trigger(0)

        self.ncb = self.noise.irq(handler=ncbf,
                                 trigger=self.noise.IRQ_RISING)

    def stop(self):
        #self.scb = self.sense.irq(handler=None,
        #                         trigger=None)
        self.scb.trigger(0)
        
    def mirror(self):
        while True:
            self.led(self.sense())

    def bip(self):
        self.led(0)
        self.led(1)

    def show_counter(self):
        try:
            v = -1
            while True:
                while self.counter == v:
                    idle()
                v = self.counter
                print(v, end='\r')
                #t.sleep_ms(100)
        except KeyboardInterrupt:
            print()


class GLog:
    def __init__(self, geiger):
        self.geiger = geiger
        self.tim = Timer(-1)
        self.acc = Accumulator()
        self.display = False

    def start(self):
        self.prior_count = self.geiger.counter
        self.tim.init(period=1000,
                      mode=Timer.PERIODIC,
                      callback=self.log)

    def stop(self):
        self.tim.deinit()

    def log(self, t):
        # FIXME: Is there a problem when counter exceeds 2^31?
        # ... Should we zero out counter here?
        c = self.geiger.counter
        delta = c - self.prior_count
        self.prior_count = c
        self.acc.log_value(delta)
        if self.display:
            print('\x1b[s\x1b[1;74H\x1b[2K', end='')
            print(delta, c, end='\x1b[u')


class GReportPeriodically:
    def __init__(self, g, log, host='192.168.32.69'):
        self.tim = Timer(-1)
        self.reporter = Reporter(g, host, log)
        self.display = False

    def start(self):
        self.tim.init(period=2000,
                      mode=Timer.PERIODIC,
                      callback=self.report)

    def stop(self):
        self.tim.deinit()

    def report(self, t):
        self.reporter.send()


class Gwsgi:
    def __init__(self, log):
        self.log = log
        self.count = 0
        self.welcome = b"Geiger counter quick demo\n"

    def wsgi_app(self, environ, start_response):
        def yb():
            yield self.welcome
            yield b'Queried %d times\n' % self.count
            yield from self.y_vals()

        self.count += 1


        if environ['PATH_INFO'] == '/favicon.ico':
            status = '404 not found'
            response_headers = [('Content-type', 'text/plain')]
            rv = []
        else:
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            rv = [self.welcome, b'%d\n'%self.count]
            rv = yb()
        start_response(status, response_headers)
        return rv

    def y_vals(self):
        yield "seconds: "
        for v in self.log.acc.s.last_n(60):
            yield b' %d' % v
        yield "\nminutes: "
        for v in self.log.acc.m.last_n(60):
            yield b' %d' % v
        yield "\nhours: "
        for v in self.log.acc.h.last_n(60):
            yield b' %d' % v
        yield "\ndays: "
        for v in self.log.acc.d.last_n(60):
            yield b' %d' % v
