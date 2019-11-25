from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import logging
import logging.config
import yaml

# app configurations by yaml
with open('./app.yaml') as f:
    app_conf = yaml.load(f,Loader=yaml.FullLoader)

# logger
logging.config.fileConfig("logger.conf")
logger = logging.getLogger(app_conf['logger']['qualname'])

# multy threads
thread_excutor = ThreadPoolExecutor()

# multy process
process_excutor = ProcessPoolExecutor()
