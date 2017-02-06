# t1- TAS

import micropython
import machine as m
from time import sleep_us

micropython.alloc_emergency_exception_buf(100)

class T1:
    def __init__(self):
        self.led = m.Pin(0, mode=m.Pin.OUT)
        self.sense = m.Pin(4, mode=m.Pin.IN)
        self.cb = None
        self.counter = 0

    def start(self):
        if self.cb:
            self.cb.trigger(self.sense.IRQ_RISING)
            return

        def cbf(pin):
            #was = m.disable_irq() # for demonstration
            self.counter += 1
            self.bip()
            #m.enable_irq(was)   # restore
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
                    m.idle()
                v = self.counter
                print(v, end='\r')
                #sleep_ms(100)
        except KeyboardInterrupt:
            print()



import t1
import unittest
import machine as m

class TestT1(unittest.TestCase):

    def testInit(self):
        tt = T1()
        self.assertEqual(tt.counter, 0)
        self.assertIsInstance(tt.led, m.Pin)
        self.assertIsInstance(tt.sense, m.Pin)

    def testCounter(self):
        # requires a jumper from pin 4 to pin 5
        tt = T1()
        signal_gen = m.Pin(5, m.Pin.OUT, 0)
        self.assertEqual(tt.counter, 0)

        #until start()ed, counter does not advance
        signal_gen(1)
        self.assertEqual(tt.counter, 0)
        signal_gen(0)
        self.assertEqual(tt.counter, 0)

        #once start()ed, counter advances
        tt.start()
        self.assertEqual(tt.counter, 0)
        signal_gen(1)           # on rising edge
        sleep_us(1000)
        self.assertEqual(tt.counter, 1)
        signal_gen(0)           # but not on falling edge
        sleep_us(1000)
        self.assertEqual(tt.counter, 1)

        # Again by one
        signal_gen(1)           # on rising edge
        sleep_us(1000)
        self.assertEqual(tt.counter, 2)
        signal_gen(0)           # but not on falling edge
        sleep_us(1000)
        self.assertEqual(tt.counter, 2)

        # one each time
        c = tt.counter + 1
        for i in range(100):
            signal_gen(1)
            signal_gen(0)
            sleep_us(1000)
            self.assertEqual(tt.counter, i+c)
