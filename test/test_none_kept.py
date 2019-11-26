from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor

import unittest
from unittest import TestCase
from glo import logger

class TestNoneKept(TestCase):
    
    def test_code(self):
        logger.debug('test_code')
        str = '20191125085018/909/1.jpg'
        s=str[0:str.rindex('/')]
        s1=str[len(s)+1:len(str)]
        logger.debug(s+s1)
    
    total = 1
    def test_process_excutor(self):
        logger.debug('')
        def log(text,):
            self.total = self.total + 1
            logger.debug('ProcessPoolExecutor %s' % text)
        with ProcessPoolExecutor() as excutor:
            for i in range(1,10):
                excutor.submit(log(str(i)))
        logger.debug('Total %d',self.total)