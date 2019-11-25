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
        logger.debug(s)