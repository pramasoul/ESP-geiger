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


from faker.providers import BaseProvider
from faker.generator import random
fake = faker.Faker()

class PacketProvider(BaseProvider):
    """
    A Provider of fake UDPListener()-received radiation sensor packets
    """
    def port(self):
        return random.randrange(1<<16)

    def timestamp(self):
        return fake.unix_time() + round(random.random(), 6)

    def packet(self):
        l_data = random.randrange(200,600)
        data = bytes(random.randrange(1<<8) for i in range(l_data))
        addr = fake.ipv4(), self.port()
        return self.timestamp(), addr, data


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
        self.fake = faker.Factory.create()
        self.fake.add_provider(PacketProvider)
        self.fake.seed('something repeatable')

    def tearDown(self):
        pass

    def testFakePacket(self):
        p = self.fake.packet()
        self.assertEqual(len(p), 3)
        ts, addr, data = p
        self.assertIsInstance(ts, float)
        self.assertEqual(len(addr), 2)
        ip, port = addr
        self.assertIsInstance(ip, str)
        self.assertIsInstance(port, int)
        self.assertIsInstance(data, bytes)


    def testInit(self):
        with tempfile.NamedTemporaryFile(suffix='.j') as f:
            j = Journal(f.name)
            self.assertIsInstance(j, Journal)

    def sequentialTest(self, f):
        j = Journal(f.name)
        self.assertIsInstance(j, Journal)
        pkts = [self.fake.packet() for i in range(100)]
        for p in pkts:
            j.record(p)
        j.flush()
        self.assertEqual(list(j), pkts)

    def testRecordUncompressed(self):
        with tempfile.NamedTemporaryFile(suffix='.j') as f:
            self.sequentialTest(f)

    def testRecordCompressed(self):
        with tempfile.NamedTemporaryFile(suffix='.jgz') as f:
            self.sequentialTest(f)

if __name__ == '__main__':
    unittest.main()
