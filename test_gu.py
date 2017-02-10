# test Geiger utilities - TAS
# Some of these tests are too demanding to run on a microplatform
# They should all pass in cPython on a computer

import unittest
from random import randrange

from gu import Accumulator, Strip
from guts import CanonicalAccumulator

class TestStrip(unittest.TestCase):
    def testInit(self):
        s = Strip('H', 13, 45)
        self.assertIsInstance(s, Strip)

    def testStores(self):
        s = Strip('H', 13, 45)
        for i in range(123):
            s.note(i+1)

    def testYields(self):
        s = Strip('H', 13, 45)
        for i in range(10):
            s.note(i+1)
        self.assertEqual(list(s.last_n(3)), list(range(10, 7, -1)))
        self.assertEqual(list(s.last_n(10)), list(range(10, 0, -1)))
        self.assertEqual(list(s.last_n(100)), list(range(10, 0, -1)))


class TestCanonicalAccumulator(unittest.TestCase):

    def testInit(self):
        a = CanonicalAccumulator()
        self.assertIsInstance(a, CanonicalAccumulator)

    def testStores(self):
        a = CanonicalAccumulator()
        for i in range(1000):
            a.log_value(i)

    def testYields(self):
        a = CanonicalAccumulator()
        for i in range(10):
            a.log_value(i+1)
        self.assertEqual(list(a.last_n_seconds(10)), list(range(10,0,-1)))
        self.assertEqual(list(a.last_n_seconds(100)), list(range(10,0,-1)))

    def testYields2(self):
        a = CanonicalAccumulator()
        for i in range(400):
            a.log_value(i+1)
        self.assertEqual(list(a.last_n_seconds(10)), list(range(400,390,-1)))
        self.assertEqual(list(a.last_n_seconds(300)), list(range(400,100,-1)))


    def testYieldm(self):
        a = CanonicalAccumulator()
        for i in range(59):
            a.log_value(i+1)
        self.assertEqual(list(a.last_n_minutes(10)), [])
        a.log_value(60)
        t = sum(range(60,0,-1))
        self.assertEqual(t, 60*61/2)
        self.assertEqual(list(a.last_n_minutes(10)), [t])
        for i in range(60):
            a.log_value(i+61)
        self.assertEqual(list(a.last_n_minutes(10)), [t+3600, t])
        

    def testYieldDaysWorth(self):
        a = CanonicalAccumulator()
        n = 60*60*24*2
        for i in range(n):
            a.log_value(i+1)
        self.assertEqual(list(a.last_n_seconds(12345)), list(range(n,n-300,-1)))
        # check minutes
        b = 60
        m = n//b
        t = b*(b-1)//2
        self.assertEqual(list(a.last_n_minutes(3))[0], b*n-t)
        self.assertEqual(list(a.last_n_minutes(12345)),
                         list(range(b*b*m-t, b*b*(m-300)-t, -b*b)))
        # check hours
        b *= 60
        m = n//b
        t = b*(b-1)//2
        self.assertEqual(list(a.last_n_hours(12345)),
                         list(range(b*b*m-t, b*b*(m-48)-t, -b*b)))
        # check days
        b *= 24
        m = n//b
        t = b*(b-1)//2
        self.assertEqual(list(a.last_n_days(12345)),
                         list(range(b*b*m-t, b*b*(m-2)-t, -b*b)))


def radioactive(n):
    #random.seed("repeatable")
    for i in range(n):
        yield randrange(1<<16)

class TestAccumulator(unittest.TestCase):

    def testInit(self):
        a = Accumulator()
        self.assertIsInstance(a, Accumulator)

    def testStores(self):
        a = Accumulator()
        for i in range(1000):
            a.log_value(i)

    def testYields(self):
        a = Accumulator()
        for i in range(10):
            a.log_value(i+1)
        self.assertEqual(list(a.last_n_seconds(10)), list(range(10,0,-1)))
        self.assertEqual(list(a.last_n_seconds(100)), list(range(10,-0,-1)))

    def testYields2(self):
        a = Accumulator()
        for i in range(400):
            a.log_value(i+1)
        self.assertEqual(list(a.last_n_seconds(10)), list(range(400,390,-1)))
        self.assertEqual(list(a.last_n_seconds(300)), list(range(400,100,-1)))


    def testYieldm(self):
        a = Accumulator()
        for i in range(59):
            a.log_value(i+1)
        self.assertEqual(list(a.last_n_minutes(10)), [])
        a.log_value(60)
        t = sum(range(60,0,-1))
        self.assertEqual(t, 60*61/2)
        self.assertEqual(list(a.last_n_minutes(10)), [t])
        for i in range(60):
            a.log_value(i+61)
        self.assertEqual(list(a.last_n_minutes(10)), [t+3600, t])
        

    def testAgainstCanon(self):
        def feed(n):
            for i in radioactive(n):
                a.log_value(i)
                c.log_value(i)

        def compare():
            self.assertEqual(list(a.last_n_seconds(12345)),
                             list(c.last_n_seconds(12345)))
            # check minutes
            self.assertEqual(list(a.last_n_minutes(12345)),
                             list(c.last_n_minutes(12345)))
            # check hours
            self.assertEqual(list(a.last_n_hours(12345)),
                             list(c.last_n_hours(12345)))
            # check days
            self.assertEqual(list(a.last_n_days(12345)),
                             list(c.last_n_days(12345)))


        a = Accumulator()
        c = CanonicalAccumulator()
        for n in (58,1,1,1,1):
            feed(n)
            compare()
        for i in range(1,1000):
            feed(randrange(i))
            compare()


if __name__ == '__main__':
    unittest.main()
