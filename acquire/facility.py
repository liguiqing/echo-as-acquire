from config import logger

class Facility:
    """采集设备
    所有采集设备均为此类子类
    """
    def play(self,batch=None,*args):
        """进行采集
        Args:
            batch: 采集批次,默认新建设一批次
            args: 采集时所须的其他参数
        """
        pass
    def set_args(self,config=None,*args):
        """设置采集设备的参数
        Args:
            config: 参数配置
        """
        pass                 

class FacilityFactory:
    """采集设备分类工厂
    所有采集设备分类均为此类子类,在本级目录新建一个子目录处理各种采集设备

    """

    def get_connected(self, product_name, image_acquired=lambda acquired: None):
        """获取已经连接到计算机的设备
        Args:
            product_name: 设备名称
            image_acquired: 每一张图片采集成功后的回调函数
        Returns:
            an instance of fact Facility
        """
        pass
    
    def list_installed(self):
        """取得已经安装到计算机的设备"""
        pass

    def close(self, product_name):
        """释放设备
        Args:
            product_name: 将要释放的设备名称
        """
        pass

    def terminate(self):
        """终止工厂服务"""
        pass


class FacilityFactoryMocker(FacilityFactory):
    """模拟对象"""
    def __init__(self):
        self.type = 'mocker'

    def __hash__(self):
        return hash(id(self.type))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(id(self.type))==hash(id(other.type))
        else:
            return False

    def list_installed(self):
        return ['mocker']

    def get_connected(self, product_name, image_acquired=lambda acquired: None):
        return Facility()

    def close(self):
        logger.debug('Acquire facility closed')

    def terminate(self):
        logger.debug('Acquire facility terminate')
