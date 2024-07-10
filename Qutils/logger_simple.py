import logging

logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG) 
handler = logging.StreamHandler() 
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)-40s |')
handler.setFormatter(formatter)
logger.addHandler(handler)



if __name__=='__main__':
    logger.info('hi')
    logger.debug('hihi')