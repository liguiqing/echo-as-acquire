from enum import Enum, unique

from acquire.facility import Facility
import acquire.scanner.twain as twain
from config import logger


class ScannerIsNotReady(Exception):
    pass

class StatusIsNotAllowed(Exception):
    pass

def default_scan_finished():
    logger.debug('Scan finished')

@unique
class PixelType(Enum):
    BW = twain.TWPT_BW
    GRAY = twain.TWPT_GRAY
    COLOR = twain.TWPT_RGB

class ScannerConfig:
    def __init__(self):
        self.is_two_sided = False
        self.dpi = 150
        self.dpp = 8
        self.pixel_type = PixelType.GRAY.value
        self.img_format = "bmp"

class Scanner(Facility):
    """采集设备--扫描仪
   扫描仪采用twain驱动连接
   扫描一张图像完成后，输出为bmp图像字节流

   Attributes:
       sd: twain.Source
       product_name：扫描仪在设备管理器中的名称
       config: 扫描参数配置
       has_capabilited： 是否已经进行扫描参数设置
       batch：所属扫描批次
       scan_finished：批次扫描完成后的回调函数
    
    """
    sd = None
    product_name = 'EPSON DS-510'
    config = None
    has_capabilited = False
    batch = None
    scan_finished = None

    def __init__(self, sd, scan_finished=None):
        """Construct of Scanner
        Args:
            sd: a instance of twain.Source
            scan_finished: 完成一次扫描后回调函数 default is default_scan_finished

        """
        self.sd = sd
        self.config = ScannerConfig()
        self.scan_finished = scan_finished if scan_finished else default_scan_finished
        self._scanning = False
        self._last_image_info = None
        
    def set_scan_finished(self, scan_finished):
        self.scan_finished = scan_finished

    def processXFer1(self):
        (handle, more_to_come) = self.sd.xfer_image_natively()
        stream = twain.dib_to_bm_file(handle)
        self.batch.append(stream,image_info=self._last_image_info)

        if more_to_come: 
            self.processXFer1()
        else:
            self._clean()

    def processXFer(self):
        def before(image_info):
            self._last_image_info = image_info
            logger.debug("Acquire image's spec {}".format(self._last_image_info))

        def after(image,more_to_come):
            if not more_to_come: 
                self._clean()
            else:
                stream = image.to_bytes()
                image.close()
                self.batch.append(stream,image_info=self._last_image_info)
            
        self.sd.acquire_natively(after,before=lambda image_info:before(image_info),show_ui=False)

    def set_args(self, config):
        """设置扫描仪参数
        Args: 
            coinfig: instance ScannerConfig

        """
        self.config = config
        dpi = config.dpi if hasattr(config,'dpi') else 150
        bpp = config.bpp if hasattr(config,'bpp') else 8
        pixel_type = config.pixel_type if hasattr(config,'pixel_type') else PixelType.GRAY.value
        
        try:
            self.sd.set_capability(twain.ICAP_PIXELTYPE, twain.TWTY_UINT16, pixel_type)
            self.sd.set_capability(twain.ICAP_UNITS, twain.TWTY_UINT16, twain.TWUN_INCHES)
            if bpp:
                self.sd.set_capability(twain.ICAP_BITDEPTH, twain.TWTY_UINT16, bpp)
            if dpi:
                self.sd.set_capability(twain.ICAP_XRESOLUTION, twain.TWTY_FIX32, dpi)
                self.sd.set_capability(twain.ICAP_YRESOLUTION, twain.TWTY_FIX32, dpi)
            self.sd.set_capability(twain.ICAP_XFERMECH, twain.TWTY_UINT16, twain.TWSX_NATIVE)

        except StatusIsNotAllowed:
            pass

    def play(self, batch = None):
        if self.sd is None :
            raise ScannerIsNotReady
        
        if self._scanning :
           return

        self._scanning = True

        if not self.has_capabilited :
            self.set_args(ScannerConfig())
            self.has_capabilited = True

        self.batch = batch if batch else BatchMocker()
        logger.debug("Scan starting ...")
        self.sd.request_acquire(0, 0)
        self.processXFer()

    def terminate(self):
        self.sd.destroy()
        self.sd=None
    
    def _clean(self):
        self._last_image_info = None
        self.scan_finished()
        self._scanning = False

class BatchMocker:
    def append(self, stream, image_info):
        logger.debug('Acquire image {}'.format(image_info))
