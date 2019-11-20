#!%PYTHON_HOMR/python
import gevent
import signal

from config import logger

import local_http_server as server

def handler_sigquit():
    logger.debug('Shutdowning...')
    server.shutdown()
    gevent.kill(gevent.getcurrent())
    gevent.sleep(0)

def main():
    logger.debug("Scan Server startup  ...")
    server.startup()
    logger.debug("Scan Server started")
    gevent.signal(signal.signal, handler_sigquit)

def __del(self):
    server.shutdown()

if __name__ == '__main__':
    main()