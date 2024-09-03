from abc import ABC, abstractmethod








class Session(ABC):
    """ >>> # 
    self.session = None
    self.restart()
    ...
    >>> # api example
    class ApiSess(Session):
        pclass = httpx.AsyncClient
        async def restart(self):
            if self.session is None:
                self.session = httpx.AsyncClient()
            else: 
                await self.session.aclose()
                self.session = httpx.AsyncClient()
    ...
    >>> # sql example
    class SqlSess(Session):
        async def restart(self):
            pclass = AsyncConnectionPool
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
    async def x_start(self):
        pass
    @abstractmethod
    async def x_close(self):
        pass
    @abstractmethod
    async def x_reset(self):
        pass

try:
    # ------------------------------------------------------------------------ #
    import httpx
    # ------------------------------------------------------------------------ #
    class ApiSess(Session):
        pclass = httpx.AsyncClient

        def __init__(self):
            self.session=None

        # ------------------------------------------------------------------------ #
        async def x_start(self):
            try:
                self.session = httpx.AsyncClient()
            except Exception as e:
                print(e)

        # ------------------------------------------------------------------------ #
        async def x_close(self):
            try:
                await self.session.aclose()
            except Exception as e:
                print(e)
            
        # ------------------------------------------------------------------------ #
        async def x_reset(self):
            if self.session is None:
                self.session = httpx.AsyncClient()
            else: 
                await self.session.aclose()
                self.session = httpx.AsyncClient()
except Exception as e:
    print(e.__class__.__name__, e)
    class ApiSess(Session):
        pclass = None






try:
    # ------------------------------------------------------------------------ #
    from Qpgsql import Pgsql
    from Qpgsql.tools.hint import AsyncConnectionPool
    # ------------------------------------------------------------------------ #

    class SqlSess(Session):
        pclass = AsyncConnectionPool

        def __init__(self, pgsql):
            self.session = None
            self.pgsql = pgsql

        # ------------------------------------------------------------------------ #
        async def x_start(self):
            try:
                self.session = self.pgsql.xconnect_pool()
                await self.session.open()
            except Exception as e:
                print(e)

        # ------------------------------------------------------------------------ #
        async def x_close(self):
            try:
                await self.session.close()
                self.session = self.pgsql.xconnect_pool()
            except Exception as e:
                print(e)

        # ------------------------------------------------------------------------ #
        async def x_reset(self):
            if self.session is None:
                self.session = self.pgsql.xconnect_pool()
                await self.session.open()
            else: 
                await self.session.close()
                self.session = self.pgsql.xconnect_pool()
                await self.session.open()
                
except Exception as e:
    print(e.__class__.__name__, e)
    class SqlSess(Session):
        pclass = None
# import asyncio

# from Qpgsql import Pgsql

# # pgsql = Pgsql()

# async def main():
#     apisess = ApiSess()
#     await apisess.x_start()
# #     await apisess.start()

#     resp = await apisess.session.get('https://www.naver.com/')
#     print(resp)
#     await apisess.close()
# #     await apisess.close()

# #     # sqlsess = SqlSess(pgsql=pgsql)
# #     # await sqlsess.start()
# #     # await sqlsess.close()

# asyncio.run(main())

# # apisess = ApiSess()
# # apisess.restart()
# # apisess.session

# # session = httpx.AsyncClient()
# # dir(session)
# # type(apisess.session)