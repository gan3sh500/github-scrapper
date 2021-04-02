import logging
import logging.handlers
logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.handlers.RotatingFileHandler('main_logger.log', maxBytes=10_000_000, backupCount=2)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)