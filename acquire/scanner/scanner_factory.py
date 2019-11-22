import math
import os
import os.path
from datetime import datetime

from acquire.facility import FacilityFactory
import acquire.scanner.twain as twain
from acquire.scanner.scanner import Scanner
from config import logger


class ScannerFactory(FacilityFactory):
    """扫描仪管理工厂"""
    SM = None        # Source Manager
    scanners = {}

    def __init__(self):
        self.name = 'scanner'
        self.alias = '扫描仪'
        self.SM = twain.SourceManager(0, dsm_name="dll/TWAINDSM.dll")

    def __str__(self):
        return "ScannerFactory"

    def list_installed(self):
        return self.SM.source_list

    def get_connected(self, product_name=None, image_acquired=None):
        if not product_name:
            product_name = self.SM.source_list[0]
        logger.debug("Get scanner %s", product_name, exc_info=1)
        if product_name in self.scanners:
            return self.scanners[product_name]

        sd = self.SM.open_source(product_name)
        scanner = Scanner(sd)
        scanner.set_batch_finished(batch_finished = image_acquired)
        self.scanners[product_name] = scanner
        return scanner
    
    def close(self,product_name):
        scanner = self.scanners[product_name]
        if scanner:
            scanner.terminate()
            del self.scanners[product_name]

    def terminate(self):
        for v in self.scanners.values():
            v.terminate()

        if self.SM:
            self.SM.close()
        self.SM = None

class CannotWriteTransferFile(Exception):
    pass

class CancelAll(Exception):
    """Exception used by callbacks to cancel remaining image transfers"""
    pass

class CheckStatus(Exception):
    """This exception means that operation succeeded but user value was truncated
    to fit valid range
    """
    pass

def register(container):
    """注册到设备管理容器
    Args:
        container: a dict
    """
    container['scanner'] = ScannerFactory()