import os
from acquire.facility import Facility,FacilityFactory,VirtualFacilityFactory
import glo

facilities = {}

def _register_facility_components(dir):
    """动态注册采集设备组件"""
    files = os.listdir(dir)
    for file in files:
        path = os.path.join(dir, file)
        if os.path.isdir(path) and file != '__pycache__':
            _register_facility_components(path)
        else:
            if file == 'acquire_facility_factory.py':
                continue
            if file.endswith('factory.py'):
                absfile = dir + os.path.sep + file
                s = absfile.index('acquire') + 8
                e = absfile.index('.py')
                python = absfile[s: e].replace(os.sep,'.')
                glo.logger.debug("Load acquire.facility component %s " % python)
                dmf = __import__(python,fromlist = True)
                try:
                    func = getattr(dmf,'register')
                    func(facilities)
                except EnvironmentError as e:
                    raise e

def facility_register(facility):
    """采集设备注册"""
    if not hasattr(facility,'name'):
        return

    facilities[facility.name] = facility


def get_facilities_connected():
    """取得所有已经安装的采集设备
    
    Returns:
        type of list as :
        [{'facility_name':['F1','F2']}]
    """
    return [{'name':k, 'instances':facilities[k].list_installed()} for k in facilities.keys()]


def get_facility(category_name=None):
    """取得名为category_name的采集设备
    
    Arags:
        category_name: 设备分类名称

    Returns:
        A instance of FacilityFactory
    """
    if category_name is None:
        return VirtualFacilityFactory()

    for k,v in facilities.items():
        if k == category_name:
            return v

    return VirtualFacilityFactory()        


def install():
    """安装采集设备"""
    _register_facility_components(os.path.dirname(__file__))