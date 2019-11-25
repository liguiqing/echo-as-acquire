#!%PYTHON_HOME/python
import gevent
import signal

import glo

import local_http_server as server

def handler_sigquit():
    glo.logger.debug('Shutdowning...')
    server.shutdown()
    gevent.kill(gevent.getcurrent())
    gevent.sleep(0)

def main():
    glo.logger.debug("Scan Server startup  ...")
    server.startup()
    glo.logger.debug("Scan Server started")
    gevent.signal(signal.signal, handler_sigquit)

def __del(self):
    server.shutdown()

if __name__ == '__main__':
    main()