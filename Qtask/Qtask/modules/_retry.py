







from Qlogger import Logger
from typing import Literal


class Retry:
    
    def __init__(self, retry=3, delay=0.3, raise_in_drop=True, logger=None):
        self.logger:Logger=logger
        self.retry=retry
        self.delay=delay
        
        self.pre_func = None
        self.sur_func = None
        
        self._raise_in_drop = raise_in_drop
        
    def set_callback(self, pre_func=None, sur_func=None):
        self.pre_func = pre_func
        self.sur_func = sur_func
        
    def __call__(self, xdef):
        async def wrapper(*args, **kwds):
            retry=0
            while True:
                if self.pre_func is not None: await self.pre_func()
                try:
                    result = await xdef(*args, **kwds)
                    return result
                
                except Exception as e:
                    if retry < self.retry:
                        retry += 1
                        await self.backoff(retry)
                        self.msg_retry(xdef.__name__,args,retry)
                    else:
                        self.msg_drop(xdef.__name__,args,retry)
                        if self._raise_in_drop: raise e
                finally:
                    if self.sur_func is not None: await self.sur_func()  
        return wrapper
    
    async def backoff(self, retry):
        sec = round(0.3*(retry/self.retry),3)
        await asyncio.sleep(sec)
    
    # -------------------------------- logger -------------------------------- #
    def msg_retry(self,fname,args,retry):
        if self.logger is not None:
            self.logger.warning.msg(
                f'except{str(args)}',f'retry({retry})',fname=fname)
            
    def msg_drop(self,fname,args,retry):
        if self.logger is not None:
            self.logger.error.msg(
                f'except{str(args)}',f'drop',fname=fname)

if __name__ == "__main__":
    import asyncio
    logger= Logger(logname='logger',context='async')
    retry = Retry(3,delay=0.2,logger=logger)
    
        
    async def pre_fun():
        print('p')
        
    async def sur_fun():
        print('s')
        
    retry.set_callback(pre_fun,sur_fun)
        
    @retry
    async def myfun(x):
        print(x)
        raise ValueError
        
    asyncio.run(myfun(1))    
            