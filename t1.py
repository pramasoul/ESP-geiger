# t1- TAS

import micropython
import machine as m
import time as t

micropython.alloc_emergency_exception_buf(100)

class T1:
    def __init__(self):
        self.led = m.Pin(0, mode=m.Pin.OUT)
        self.sense = m.Pin(4, mode=m.Pin.IN, pull=m.Pin.PULL_UP)
        self.counter = 0

    def start(self):
        def cbf(pin):
            was = m.disable_irq() # for demonstration
            self.counter += 1
            self.bip()
            m.enable_irq(was)   # restore
        self.cb = self.sense.irq(handler=cbf,
                                 trigger=self.sense.IRQ_FALLING)

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
