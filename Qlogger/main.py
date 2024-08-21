from Qlogger import Logger, _Logger



if __name__ == "__main__":
    # ------------------------------ base logger ----------------------------- #
    logger = _Logger('test', 'head', 'log.ini', msg=True)
    logger.debug('debug')
    logger.info('info')
    logger.warning('warn')
    logger.error('error')

    # ----------------------------- custom logger ---------------------------- #

    logger = Logger('test','head')
    logger.set_clsname('child')

    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bbbbbbbbbbbbbbbbbbbbbbbbbb',)
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',paddings='-')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns='^')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns='<')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns='>')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns=['^','<','>'])
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bbbbbbbbbbbbbbbbbbbbbbbbbb',widths=(2,1))
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa')
    # logger.debug.msg('dd', offset=0.2)
    # logger.debug.msg('dd', widths=4,offset=0.2)


    # ------------------------------- subclass ------------------------------- #
    def child_func():
        logger.info.msg('aa')
    
    logger2 = Logger('temp','head')
    logger2.set_clsname('parent')


    def parent_func():
        logger2.info.msg('bb')
        logger2.set_sublogger(logger)
        child_func()

    parent_func()


