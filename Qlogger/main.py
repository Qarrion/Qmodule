from Qlogger import Logger

logger = Logger('test', 'blue', 'log.ini', False)
logger.info('info')
logger.debug('debug')
logger.warning('warn')
logger.error('error')

