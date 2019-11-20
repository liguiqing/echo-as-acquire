"""本地http服务，用以连接图像采集设备及接收客户端（浏览器-websocket）图像处理命令"""

import json
import random
import time

from queue import Queue

import gevent
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

from config import app_conf, logger
from acquire.acquire_facility_factory import facilities, get_facility,install as install_facility
# from image.image_service import Batch, ImageService
# from scan.scanner_factory import ScannerFactory


class ImageAcquire:
    """图像采集
    
    Attributes:
        facility: an instance of FacilityFactory 
        product_name: 采集设备名称
        playable: 是否可以进行采集
        batch: 采集批次
    """

    facility = None
    product_name = None
    playable = False
    batch = None

    _run = True

    def start(self):
        """启动图像采集"""
        logger.debug('Image Acquire started')
        while True:
            if not self._run:
                break

            gevent.sleep(0.1)
            if self.facility is None:
                continue

            if self.playable:
                self.playable = False
                logger.debug('Acquire with {}'.format(self.product_name))
                self.facility.get_connected(self.product_name).play(batch=self.batch)

    def stop(self):
        self.facility = None
        self.product_name = None
        self.playable = None
        self.batch = None
        self._run = False

    def play(self):
        self.playable = True

    def pause(self):
        self.playable = False

    def set_facility(self, facility, product_name=""):
        self.facility = facility
        self.product_name = product_name

    def get_status(self):
        return not self.playable    


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
    """flask_io.emit 消息缓冲器
    
    Attributes:

    """
    _buffer = Queue(maxsize=5000)

    def put(self, on, data):
        self._buffer.put_nowait(EmitMessage(on=on, data=data))

    def over(self):
        self.put('over',{'success': True})

    def get(self):
        return self._buffer.get_nowait()
    
    def size(self):
        return self._buffer.qsize()

    def clean(self):
        pass

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
            logger.warn("Not any more emit message! ")
            continue

        logger.debug("Emit message %s", msg, exc_info=1)
        if msg.namespace:
            socketio.emit(msg.on, msg.data, namespace=msg.namespace)
        else:
            socketio.emit(msg.on, msg.data)


def task_acquire():
    acquire.start()


def startup():
    gevent.joinall([gevent.spawn(task_start_flask),
                    gevent.spawn(task_flaskio_emit),
                    gevent.spawn(task_acquire),
                    ])


def shutdown():
    acquire.facility.close()

    # shutdown flask http server
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def batch_acquire_finished():
    """批量采集完成回调函数"""
    logger.debug('A batch acquire is over ')
    emit_message_buffer.over()
    acquire.pause()


def publish_image_acquired(image):
    """单张图像采集完成
    Args:
        image: object 图像
    """
    emit_message_buffer.put('acquired',image.__dict__)

@socketio.on_error_default
def default_error_handler(e):
    logger.debug('Scoket Error message %s',
                 request.event["message"], exc_info=1)
    logger.debug('Scoket Error args %s', request.event["args"], exc_info=1)

@app.route('/acquire/facilities', methods=['GET'])
def list_facilities():
    """获取已经连接到计算机的采集设备"""
    logger.debug('Installed facilities %s', facilities, exc_info=1)
    return jsonify(facilities.keys())

@app.route('/acquire/facility/<facility_type>/<product_name>', methods=['GET'])
def some_online_facility(facility_type,product_name):
    """获取某种采集设备"""
    facility_factory = get_facility(facility_type)
    acquire.set_facility(facility_factory,product_name=product_name)
    logger.debug('Get installed  %s', facility_type, exc_info=1)
    return jsonify({'name':facility_factory.name})


@app.route('/acquire/scanner/selected/<product_name>', methods=['GET'])
def selected_scanner(product_name):
    """选择扫描仪
    Arags: 
        product_name: 扫描在计算机设备管理器中的名称
    """
    logger.debug('Scan use %s', product_name, exc_info=1)
    scanner = acquire.facility.get_instance(product_name=product_name)
    # scanner.set_image_writed(image_writed)
    scanner.set_scan_finished(batch_acquire_finished)
    logger.debug("Acquire facility si %s ", product_name, exc_info=1)
    acquire.set_facility(scanner,product_name=product_name)
    return jsonify({"success": True})


@app.route('/acquire/scanner/realease/<product_name>', methods=['GET'])
def realease_scanner(product_name):
    logger.debug('Scan use %s', product_name, exc_info=1)
    # acquire.stop()
    # sf.realease(product_name)
    return jsonify({"success": True})


@app.route('/acquire/scanner/status', methods=['GET'])
def status_scanner():
    logger.debug('acquire facility status ')
    return jsonify({"acquireStatus": acquire.get_status()})


@app.route('/acquire/scanner/scanningImage', methods=['GET'])
def get_scanning_image():
    logger.debug('Get scanning image')
    try:
        image = scanning_image_buffer.get()
    except:
        logger.warn("Not any more image ")
    
    if image :
        return jsonify({"data": image.__dict__})
    else :
        return jsonify({"data": {"path":None}})


@socketio.on('acquire',namespace='scanner')
def acquire_connect(data):
    logger.debug("Websocket acquiring connected %s", data, exc_info=1)
    # acquire.appendTo(Batch(image_writed=image_writed))
    # acquire.batch = Batch()
    acquire.play()


@socketio.on('connect')
def acquiring_connect():
    logger.debug("Websocket acquiring connected ")


@socketio.on('disconnect')
def acquiring_disconnect():
    logger.debug("Websocket acquiring disconnected ")
