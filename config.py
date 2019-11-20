import logging
import logging.config
import yaml

with open('./app.yaml') as f:
    app_conf = yaml.load(f,Loader=yaml.FullLoader)


logging.config.fileConfig("logger.conf")
logger = logging.getLogger(app_conf['logger']['qualname'])
