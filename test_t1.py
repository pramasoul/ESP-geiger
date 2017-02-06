# t1- TAS
import micropython
micropython.alloc_emergency_exception_buf(100)
import machine as m
from time import sleep_us
from t1 import T1
import unittest

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
