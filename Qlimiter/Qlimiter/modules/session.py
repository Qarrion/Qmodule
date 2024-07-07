
from abc import ABC, abstractmethod

from typing import Callable
import httpx

# TODO

class Session(ABC):
    """ >>> # 
    self.xconn = None
    self.restart()
    """
    def __init__(self):
        self.xconn = None

    @abstractmethod
    async def restart(self):
        pass



class Xsession:
    def __init__(self, xconnector:Callable, close_method:str, close_status:str):
        self.xconnector = xconnector
        self.xconn = None
        self._close_method_name = close_method
        self._close_status_name = close_status


    async def restart(self):
        await self.close()
        await self.start()

    async def start(self):
        self.xconn = await self.xconnector()
    # def start(self):
    #     self.xconn = self.xconnector()
        
    async def close(self):
        if self.xconn is not None:
            await getattr(self.xconn,self._close_method_name)()
            self.xconn = None
        elif getattr(self.xconn, self._close_status_name):
            self.xconn = None
    # async def close(self):
    #     if self.xconn is not None:
    #         await getattr(self.xconn,self._close_method_name)()
    #         self.xconn = None
    #     elif getattr(self.xconn, self._close_status_name):
    #         self.xconn = None
    
        
class Xclient:

    def __init__(self):
        self.xpool:httpx.AsyncClient = None

    def start(self):
        self.xpool = httpx.AsyncClient()

    async def restart(self):
        if self.xpool is not None:
            await self.xpool.aclose()
        self.xpool = httpx.AsyncClient()
        print('restart')

    async def close_client(self):
        if self.xpool is not None:
            await self.xpool.aclose()
            print(self.xpool.is_closed)
            self.xpool = None
            


# xc = Xclient()
# xc.start()
# print(xc.xpool)
# print(xc.close_client())
# # print(getattr(xc.xpool,'aclose'))
# httpx.AsyncClient().is_closed