"""本地http服务，用以连接图像采集设备及接收客户端（浏览器-websocket）图像采集及图像处理命令"""

from PIL import Image
import json
import random
import os
import os.path
import time

from queue import Queue

import gevent
from flask import Flask, jsonify, request,send_from_directory
from flask_socketio import SocketIO, emit

from acquire.acquire_facility_factory import get_facilities_connected, get_facility,install as install_facility
from glo import logger,app_conf
from image.image_service import get_image_handler

class ImageAcquire:
    """图像采集

    Attributes:
        facility: an instance of FacilityFactory 
        product_name: 采集设备名称
        playable: 是否可以进行采集
        image_handler: 图像处理器
    """

    facility = None
    product_name = None
    playable = False
    image_handler = None

    def _do_play(self):
        if self.playable:
            self.playable = False
            logger.debug('Acquire with {}'.format(self.product_name))
            fi = self.facility.get_connected(self.product_name)
            fi.set_batch_finished(lambda: emit_message_buffer.over())
            fi.set_failure_callback(lambda: emit_message_buffer.failure('10050','扫描仪异常，请查检设备'))
            fi.play(image_handler=self.image_handler)

    def same_product_of(self,facility_name,product_name):
        return self.facility.name == facility_name and self.product_name == product_name

    def close(self):
        """关闭采集设备"""
        self.facility.close(self.product_name)

    def stop(self):
        """停止图像采集"""
        self.facility.terminate()
        self.facility = None
        self.product_name = None
        self.playable = None
        self.image_handler = None

    def play(self,image_handler=None):
        """进行图像采集
        
        Args:
            image_handler: 图像采集批次
        """
        self.image_handler = image_handler
        self.playable = True
        self._do_play()

    def set_facility(self, facility, product_name=None):
        """设定采集设备"""
        self.facility = facility
        self.product_name = product_name

    def get_status(self):
        """获取采集设备状态"""
        product = self.facility.get_connected(self.product_name)
        if hasattr(product,'status'):
            return product.status()
        else:
            return {'connected':'false','code':-1}


class EmitMessage:
    """flask_io.emit 消息体
    Attributes:
        on:  string 发送给客户端的事件名称
        data: dict,发送到客户端的数据 
        namespace: 客户端处理响应的名称空间，默认值 None
    """
    def __init__(self, on='keep_alive', data={}, namespace=None):
        self.on = on
        self.data = data
        self.namespace = namespace

    def __str__(self):
        namespace = self.namespace if self.namespace is not None else 'None'
        return 'Emit Message :{} {} {} '.format(self.on, self.data, namespace)
    
    def __eq__(self,other):
        return self.__dict__ == other.__dict__


class EmitMessageBuffer:
    """flask_io.emit 消息缓冲器"""
    _buffer = Queue(maxsize=5000)

    def put(self, on, data):
        logger.debug("Put a messsage {} to Buffer on {}".format(data,on))
        self._buffer.put_nowait(EmitMessage(on=on, data=data))

    def over(self):
        self.put('over',{'success': True})

    def failure(self,code,message):
        self.put('failure',{'success': False,'code':code,'message':message})    

    def get(self):
        return self._buffer.get_nowait()
    
    def size(self):
        return self._buffer.qsize()

    def clean(self):
        self._buffer.empty()

# 安装采集设备
install_facility()

emit_message_buffer = EmitMessageBuffer()

flask_conf = app_conf['flask']

app = Flask(__name__, static_folder=flask_conf['static_folder'])
socketio = SocketIO(app, cors_allowed_origins="*")

acquire = ImageAcquire()

# imageService = ImageService()

def task_start_flask():
    socketio.run(app, host=flask_conf['host'], port=flask_conf['port'], debug=flask_conf['debug'])


def task_flaskio_emit():
    while True:
        gevent.sleep(0.3)
        try:
            msg = emit_message_buffer.get()
        except:
            # logger.warn("Not any more emit message! ")
            continue

        logger.debug("Emit message %s", msg, exc_info=1)
        if msg.namespace:
            socketio.emit(msg.on, msg.data, namespace=msg.namespace)
        else:
            socketio.emit(msg.on, msg.data)


def startup():
    """启动扫描后台服务"""
    gevent.joinall([gevent.spawn(task_start_flask),
                    gevent.spawn(task_flaskio_emit),
                    ])


def shutdown():
    acquire.stop()

    # shutdown flask http server
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def batch_acquire_finished():
    """批量采集完成回调函数"""
    logger.debug('A batch acquire is over ')
    emit_message_buffer.over()


def image_acquired(image):
    """单张图像采集完成
    
    Args:
        image: object 图像
    """
    emit_message_buffer.put('acquired',image.__dict__)


def retruns_success(data=None):
    """返回处理成功
    
    Args:
        data:  dict 返回到客户端的数据
    """
    return jsonify({'success':True, 'data':data})


def retruns_failure(code='-1',message='操作失败'):
    """返回处理失败
    
    Args:
        code: string 异常代码
        message: string 异常信息
    """
    return jsonify({'success':False, 'message':message, 'code':code})


@socketio.on_error_default
def default_error_handler(e):
    logger.debug('Scoket Error message %s',
                 request.event["message"], exc_info=1)
    logger.debug('Scoket Error args %s', request.event["args"], exc_info=1)


@app.route('/acquire/facilities', methods=['GET'])
def list_facilities():
    """获取已经连接到计算机的采集设备
    
    Returns:
        a json as [{'facility_name':['F1','F2']}]
    """
    logger.debug('Url: /acquire/facilities Method=GET')
    return retruns_success(get_facilities_connected())


@app.route('/acquire/connect/<facility>/<product_name>', methods=['GET'])
def connect_to_online_facility(facility,product_name):
    """连接到facility类型名为product_name采集设备
    
    Args:
        facility: 设备分类名称
        product_name: 设备名称
    Returns:
        a json as {'success':True, 'data':None}
    """
    logger.debug('Url: /acquire/connect/{}/{} Method=GET'.format(facility,product_name))

    facility_factory = get_facility(facility)
    acquire.set_facility(facility_factory,product_name=product_name)
    logger.debug('Get %s success', product_name, exc_info=1)
    return retruns_success()


@app.route('/acquire/close/<facility>/<product_name>', methods=['GET'])
def close_facility(facility, product_name):
    """关闭采集设备
    
    Args:
        facility: 设备分类名称
        product_name: 设备名称
    Returns:
        a json as {'success':True, 'data':None} if success 
        else {'success':False, 'message':'操作失败', 'code':-1}
    """
    logger.debug('Url: /acquire/close/{}/{} Method=GET'.format(facility,product_name))
    if acquire.same_product_of(facility,product_name):
        acquire.close()
        return retruns_success()
    else:
        return retruns_failure()


@app.route('/acquire/status/<facility>/<product_name>', methods=['GET'])
def facility_status(facility,product_name):
    """读取facility类型名为product_name设备状态
    
    Args:
        facility: 设备分类名称
        product_name: 设备名称

    Returns:
        a json as [{'facility_name':['F1','F2']}]
    """    
    logger.debug('acquire facility status ')
    return retruns_success(acquire.get_status())

@app.route('/acquire/image/<path:file_name>', methods=['GET'])
def show_image(file_name):
    """显示已经采集的图片
    
    Args:
        file_name: 图片相对路径，如20191125085018/s1/1.jpg
    """
    logger.debug('Url: /acquire/image/{} Method=GET'.format(file_name))
    root_dir = app_conf['scan']['root_dir']
    
    path = file_name[0:file_name.rindex('/')]
    file = file_name[len(path)+1:len(file_name)]
    absolute_path = os.path.join(root_dir,path)
    logger.debug('Image {}/{}'.format(absolute_path,file))
    return send_from_directory(absolute_path,file) 

@socketio.on('acquire')
def acquire_image(data):
    """调用采集设备进行图像采集
    
    Args:
        data: dict of {'operator':'operator_name',batch_id:'1'}
    """
    logger.debug("Websocket acquire image by %s", data, exc_info=1)
    handler = get_image_handler(data)
    handler.set_image_writed(image_acquired)
    acquire.play(image_handler=handler)


@socketio.on('connect')
def websocket_connect():
    logger.debug("Websocket connected ")


@socketio.on('disconnect')
def websocket_disconnect():
    logger.debug("Websocket disconnected ")
