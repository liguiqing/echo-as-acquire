import os
from acquire.facility import Facility,FacilityFactory,FacilityFactoryMocker
from config import logger

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
                dmf = __import__(python,fromlist = True)
                try:
                    func = getattr(dmf,'register')
                    func(facilities)
                except EnvironmentError as e:
                    raise e

def facility_register(facility):
    if not hasattr(facility,'type'):
        return

    facilities[facility.type] = facility


def get_facilities_connected():
    connecteds = {}
    return {'scanner':['EPSON DS-510']}


def get_facility(type='mocker'):
    for k,v in facilities.items():
        if k == type:
            return v
    return FacilityFactoryMocker()        


def install():
    """安装采集设备"""
    _register_facility_components(os.path.dirname(__file__))