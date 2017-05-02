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
        self.led = Pin(0, mode=Pin.OUT)
        self.led(1)
        self.sense = Pin(4, mode=Pin.IN)
        self.cb = None
        self.counter = 0

    def start(self):
        if self.cb:
            self.cb.trigger(self.sense.IRQ_RISING)
            return

        def cbf(pin):
            #was = disable_irq() # unnecessary as we are only modifier
            self.counter += 1
            #enable_irq(was)
            self.bip()

        self.cb = self.sense.irq(handler=cbf,
                                 trigger=self.sense.IRQ_RISING)

    def stop(self):
        #self.cb = self.sense.irq(handler=None,
        #                         trigger=None)
        self.cb.trigger(0)
        
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
        c = self.geiger.counter
        delta = c - self.prior_count
        self.prior_count = c
        self.acc.log_value(delta)
        if self.display:
            print('\x1b[s\x1b[1;74H\x1b[2K', end='')
            print(delta, c, end='\x1b[u')


class GReportPeriodically:
    def __init__(self, g, log):
        self.tim = Timer(-1)
        self.reporter = Reporter(g, '192.168.32.144', log)
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
