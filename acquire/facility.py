import glo

class Facility:
    """采集设备

    所有采集设备均为此类子类
    """
    def play(self,image_handler=None,*args):
        """进行采集

        Args:
            image_handler: 图像采集成功后处理器
            args: 采集时所须的其他参数
        """
        pass

    def set_args(self,config=None,*args):
        """设置采集设备的参数

        Args:
            config: 参数配置 
        """
        pass

    def status(self):
        """设备状态
        
        Returns:
            dict as {'connected':'true','code':-1}
        """
        return {'connected':'false','code':-1}

    def set_batch_finished(self, batch_finished):
        """批量扫描完成回调
        
        Args:
            batch_finished: 回调函数
        """
        pass

    def set_failure_callback(self,failure_callback):
        """扫描过程中失败回调
        
        Args:
            failure_callback: 回调函数
        """
        pass

class FacilityFactory:
    """采集设备分类工厂
    所有采集设备分类均为此类子类,在本级目录新建一个子目录处理各种采集设备

    Arrtibutes:
        name: 分类名称，如扫描仪，摄像头等
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
        """取得已经安装到计算机的设备

        Returns: list  
        """
        pass

    def close(self, product_name):
        """释放名为 product_name 的设备

        Args:
            product_name: 将要释放的设备名称
        """
        pass

    def terminate(self):
        """终止工厂服务"""
        pass

class VirtualFacilityFactory(FacilityFactory):
    """虚拟设备,用于无设备时"""
    def __init__(self):
        self.name = 'Virtual'
        self.alias = '虚拟设备'

    def __hash__(self):
        return hash(id(self.name))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(id(self.name))==hash(id(other.name))
        else:
            return False

    def list_installed(self):
        return ['None']

    def get_connected(self, product_name, image_acquired=lambda acquired: None):
        return Facility()

    def close(self):
        glo.logger.debug('Acquire facility closed')

    def terminate(self):
        glo.logger.debug('Acquire facility terminate')
