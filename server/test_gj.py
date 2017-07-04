# test Geiger journalling etc - TAS
# -*- coding: utf-8 -*-
# Some of these tests are too demanding to run on a microplatform
# They should all pass in cPython on a computer

import faker
import tempfile
import unittest
from unittest import mock
from random import randrange

from gj import decodeReport, Journal

class TestDecodeReport(unittest.TestCase):
    # FIXME
    pass

class TestJournal(unittest.TestCase):
    # Test fixturing: reproducably-random received packets
    cc = ''.join(chr(v) for v in range(128) if chr(v).isalnum()) + '+-_.'
    def randomFilename(self):
        length = int(paretovariate(1))
        return ''.join(choice(cc) for t in range(length))



    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testInit(self):
        with tempfile.NamedTemporaryFile(suffix='.j') as f:
            j = Journal(f.name)
            self.assertIsInstance(j, Journal)

    def testRecordUncompressed(self):
        with tempfile.NamedTemporaryFile(suffix='.j') as f:
            j = Journal(f.name)
            self.assertIsInstance(j, Journal)
            


if __name__ == '__main__':
    unittest.main()
