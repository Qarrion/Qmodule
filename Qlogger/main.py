from Qlogger import Logger, Chain

logger = Logger('test', 'blue', 'log.ini', False)
logger.info('info')
logger.debug('debug')
logger.warning('warn')
logger.error('error')

chain = Chain(logger)
chain.info.log('test')
chain.debug.log('debug')
chain.warning.log('warn')
chain.error.log('error')
