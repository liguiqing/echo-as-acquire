import random
import time
import unittest
from unittest import TestCase

import glo
from glo import logger, thread_excutor


class TestGlobal(TestCase):
    
    def test_glo(self):
        self.assertEqual(glo.logger,logger)
        self.assertEqual(glo.thread_excutor ,thread_excutor)
        self.assertTrue(glo.thread_excutor==thread_excutor)

    def test_flask(self):
        self.assertEquals('127.0.0.1',glo.app_conf['flask']['host'])
        dm = __import__('acquire.scanner.scanner_factory',fromlist=True)
        dicts = {}
        func = getattr(dm,'register')
        func(dicts)
        self.assertEquals(1,len(dicts))
        self.assertTrue(glo.app_conf['scan']['asyn'])
    def test_multy_thread(self):
        def func1(input):
            time.sleep(random.randint(1,3))
            logger.debug('func1 input %s' % input)

    
        for x in range(100):
            print('X %d' % x)
            thread_excutor.submit(func1,x)
        # excutor.shutdown(wait=True)
        logger.debug('Over')
