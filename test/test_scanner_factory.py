from concurrent.futures import ProcessPoolExecutor 

import unittest
from unittest import TestCase

from acquire.scanner.scanner_factory import ScannerFactory
from acquire.scanner.scanner import Scanner
from config import logger
from image.image_service import get_image_handler

        
class Total:
    def __init__(self):
        self.total = 0
    def notify(self, image):
        self.total = self.total + 1
        

class TestScannerFactory(TestCase):
    """此测试必须要连接扫描仪"""

    def test_list_installed(self):
        self.assertTrue(True)
        scannerFactory = ScannerFactory()
        self.assertIsNotNone(scannerFactory)
        scannerFactory.terminate()
    
    def test_scanner(self):
        self.assertTrue(True)

        scannerFactory = ScannerFactory()
        scanners = scannerFactory.list_installed()
        scanner = scannerFactory.get_connected(scanners[0])
        scanner.set_failure_callback(lambda : logger.debug("Test failure"))
        scanner.set_batch_finished(lambda : logger.debug("Test batch finished"))
        try:
            t = Total()
            scanner.play(image_handler = get_image_handler({}))
            logger.debug(t.total)
        finally:
            scannerFactory.terminate()
        # scanner = Scanner({})