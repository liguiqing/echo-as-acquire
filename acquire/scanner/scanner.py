from enum import Enum, unique

from acquire.facility import Facility
import acquire.scanner.twain as twain
from config import logger


def _submit_image_data(handler, image_data):
    logger.debug('Handler an image %s' % image_data)
    handler.notify(image_data)


class ScannerIsNotReady(Exception):
    pass


class StatusIsNotAllowed(Exception):
    pass


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

    扫描一张图像完成后，并输出bmp图像字节流到handler中

    Attributes:
       sd: twain.Source
       product_name：扫描仪在设备管理器中的名称
       config: 扫描参数配置
       has_capabilited： 是否已经进行扫描参数设置
       handler：图像处理器

    """
    sd = None
    product_name = 'EPSON DS-510'
    config = None
    has_capabilited = False
    handler = None
    scan_finished = None

    def __init__(self, sd):
        """Construct of Scanner
        Args:
            sd: a instance of twain.Source
        """
        self.sd = sd
        self.config = ScannerConfig()
        self.batch_finished = lambda:logger.debug('Scan finished')
        self._scanning = False
        self._last_image_info = None
        self.failure_callback = lambda : logger.warn("Scanning failure!")
        
    def set_batch_finished(self, batch_finished):
        self.scan_finished = batch_finished if batch_finished else lambda:logger.debug('Scan finished')

    def set_failure_callback(self,failure_callback):
        self.failure_callback = failure_callback if failure_callback else lambda:logger.debug('Scan finished')

    def processXFer1(self):
        (handle, more_to_come) = self.sd.xfer_image_natively()
        stream = twain.dib_to_bm_file(handle)
        self.handler.notify({'data':stream, 'desc':None})
 
        if more_to_come: 
            self.processXFer1()
        else:
            self._clean()

    def processXFer(self):
        # TODO 数量会少，扫一张的时候会出现读取下一张的提示
        def before(image_info):
            self._last_image_info = image_info

        def after(image,more_to_come):
            if not more_to_come: 
                self._clean()
            else:
                stream = image.to_bytes()
                image.close()
                self.handler.notify({'data':stream, 'desc':self._last_image_info})
            
        self.sd.acquire_natively(after,before=lambda image_info:before(image_info),show_ui=False)
    
    def _publish_image(self,image):


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

    def play(self, image_handler=None):
        """进行扫描
        
        Args:
            handler: 图像处理器
        
        """
        if self.sd is None :
            raise ScannerIsNotReady
        
        if self._scanning :
           return

        self._scanning = True

        if not self.has_capabilited :
            self.set_args(ScannerConfig())
            self.has_capabilited = True

        self.handler = image_handler if image_handler else ImageHandler()
        logger.debug("Scan starting ...")
        self.sd.request_acquire(0, 0)
        try:
            self.processXFer1()
        except Exception as e:
            logger.error(e)
            self._clean(succed=False)

    def terminate(self):
        self.sd.destroy()
        self.sd=None
    
    def status(self):
        """扫描仪状态
        
        Returns:
            dict as {'connected':True,'code':10001}
        """
        return {'connected':True,'code':10001}

    def _clean(self,succed=True):
        self._last_image_info = None
        self._scanning = False
        if succed:
            self.scan_finished()
        else:
            self.failure_callback()    


class ImageHandler:
    def notify(self, image):
        logger.debug('Handler image %s',image['desc'])
