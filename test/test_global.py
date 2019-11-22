import glo
from glo import logger,thread_excutor

import unittest
from unittest import TestCase

class TestGlobal(TestCase):
    
    def test_multy_thread(self):
        def func1(input):
            logger.debug('func1 input %s' % input)

    
        for x in range(100):
            print('X %d' % x)
            thread_excutor.submit(func1,x)
        # excutor.shutdown(wait=True)
        logger.debug('Over')