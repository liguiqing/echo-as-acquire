import unittest
from unittest import TestCase

from config import app_conf, logger

class TestConfig(TestCase):

    def test_flask(self):
        self.assertEquals('127.0.0.1',app_conf['flask']['host'])
        dm = __import__('acquire.scanner.scanner_factory',fromlist=True)
        dicts = {}
        func = getattr(dm,'register')
        func(dicts)
        self.assertEquals(1,len(dicts))