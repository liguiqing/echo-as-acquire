from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor

import unittest
from unittest import TestCase
from config import logger

class TestNoneKept(TestCase):
    
    def test_multy_thread(self):
        logger.debug('TestNoneKept.test_multy_procesor')
        def func1(input):
            logger.debug('func1 input %s' % input)

        excutor = ThreadPoolExecutor()
        for x in range(100):
            logger.debug('X %d' % x)
            excutor.submit(func1,x)
        # excutor.shutdown(wait=True)
        logger.debug('Over')