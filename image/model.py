import math
import os
import os.path
import time
import io
from datetime import datetime
from queue import Queue

from PIL import Image

from config import app_conf, logger


class Img:
    def __init__(self, path='', width=0, height=0, format='bmp', pix_type='gray'):
        self.path = path
        self.width = width
        self.height = height
        self.format = format
        self.pixel_type = pix_type


def default_named_batch_folder():
    """以时间戳(YYYYmmddHHMMSS)命名目录"""
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S")
    

def default_named_image_file(total,two_sided=False):
    """给扫描图像取名
    :param totalScanned 同一批次已扫描数 >= 1
    :keyword two_sided 是否双面扫描 default is False

    """
    if not two_sided:
        return str(total)
    else:
        if total==1:
            return '1_1'
        if total==2:
            return '1_2'
        remain = 2 if total%2 == 0 else 1
        return str(math.ceil(total/2)) + '_' + str(remain)

def default_image_writed(img):
    logger.debug("Image writed {}".format(img.__dict__))


class BatchHanlder:
    """图像批次采集处理器
    

    Attributes:
        operator:
        scan_time:
        total:
        folder:
        imgs
      
    """
    operator = 'Anon'
    scan_time = datetime.now()
    total = 0
    folder = None
    imgs = []

    def __init__(self, is_two_sided=False, target_format='jpg', named_batch_folder=None,
            named_image_file=None, image_writed=None):
        self._root_dir = app_conf['scan']['root_dir']
        self._is_two_sided = is_two_sided
        self._target_format = target_format
        self.named_batch_folder = named_batch_folder if named_batch_folder else default_named_batch_folder
        self.named_image_file = named_image_file if named_image_file else default_named_image_file
        self.image_writed = image_writed if image_writed else default_image_writed

    def notify(self,image_data):
        self._add()
        logger.debug("Handler a image data %s" % image_data['desc'])
        img  = Image.open(io.BytesIO(image_data['data']))
        self._to_disk(img)

    def _to_disk(self,img):
        if self.folder is None:
            self._create_folder(self.named_batch_folder())

        file_name = self.named_image_file(self.total,self._is_two_sided)
        absolute_path = os.path.join(self.folder, "{}.{}".format(file_name,self._target_format))
        img.save(absolute_path)
        pic = Img(absolute_path)
        self.imgs.append(pic)
        self.image_writed(pic)

    def _add(self):
        self.total = self.total + 1

    def _create_folder(self,folder):
        """在文件系统中创建一个目录
        如果目录存在直接返回其绝对路径，否则创建后返回其绝对路径

        Args:
            folder: 目录名称
        
        Returns:
            目录的绝对路径
        
        Raise: None
        """
        absolute_folder = os.path.join(self._root_dir,folder)
        if not os.path.exists(absolute_folder):
            os.makedirs(absolute_folder)
        self.folder = absolute_folder
