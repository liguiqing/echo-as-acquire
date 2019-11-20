import unittest
from unittest import TestCase

from acquire.scanner.scanner_factory import ScannerFactory
from acquire.scanner.scanner import Scanner

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
        try:
            scanner.play()
        finally:
            scannerFactory.terminate()
        # scanner = Scanner({})