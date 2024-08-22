
from abc import ABC, abstractmethod

from typing import Callable
import httpx

# TODO

class Session(ABC):
    """ >>> # 
    self.session = None
    self.restart()
    ...
    >>> # api example
    class ApiSess(Session):
        pclass = AsyncClient
        async def restart(self):
            if self.session is None:
                self.session = AsyncClient()
            else: 
                await self.session.aclose()
                self.session = AsyncClient()
    ...
    >>> # sql example
    class SqlSess(Session):
    async def restart(self):
        pclcass = AsyncConnectionPool
        if self.session is None:
            self.session = pgsql.xconnect_pool()
            await self.session.open()
        else: 
            await self.session.close()
            self.session = pgsql.xconnect_pool()
            await self.session.open()
    """
    def __init__(self):
        self.session = None

    @abstractmethod
    async def restart(self):
        pass



# class Xsession:
#     def __init__(self, xconnector:Callable, close_method:str, close_status:str):
#         self.xconnector = xconnector
#         self.xconn = None
#         self._close_method_name = close_method
#         self._close_status_name = close_status


#     async def restart(self):
#         await self.close()
#         await self.start()

#     async def start(self):
#         self.xconn = await self.xconnector()
#     # def start(self):
#     #     self.xconn = self.xconnector()
        
#     async def close(self):
#         if self.xconn is not None:
#             await getattr(self.xconn,self._close_method_name)()
#             self.xconn = None
#         elif getattr(self.xconn, self._close_status_name):
#             self.xconn = None

        
# class Xclient:

#     def __init__(self):
#         self.xpool:httpx.AsyncClient = None

#     def start(self):
#         self.xpool = httpx.AsyncClient()

#     async def restart(self):
#         if self.xpool is not None:
#             await self.xpool.aclose()
#         self.xpool = httpx.AsyncClient()
#         print('restart')

#     async def close_client(self):
#         if self.xpool is not None:
#             await self.xpool.aclose()
#             print(self.xpool.is_closed)
#             self.xpool = None
            