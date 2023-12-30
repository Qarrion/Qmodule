import logging

logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG) 
handler = logging.StreamHandler() 
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

