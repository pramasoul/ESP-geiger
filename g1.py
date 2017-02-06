# g1 - geiger counter -TAS

import micropython
from machine import Pin, Timer, disable_irq, enable_irq, idle

micropython.alloc_emergency_exception_buf(100)

class Geiger:
    def __init__(self):
        self.led = Pin(0, mode=Pin.OUT)
        self.sense = Pin(4, mode=Pin.IN)
        self.cb = None
        self.counter = 0

    def start(self):
        if self.cb:
            self.cb.trigger(self.sense.IRQ_RISING)
            return

        def cbf(pin):
            was = disable_irq()
            self.counter += 1
            enable_irq(was)
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


class Foo:
    def __init__(self, g):
        self.g = g
        self.g.start()
        self.tim = Timer(-1)

    def start(self):
        self.tim.init(period=1000,
                      mode=Timer.PERIODIC,
                      callback=self.print_count)

    def stop(self):
        self.tim.deinit()

    def print_count(self, t):
        print('\x1b[s\x1b[1;70H' + str(self.g.counter) + '\x1b[u',
              end='')
