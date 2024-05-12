# -------------------------------- ver 240511 -------------------------------- #
# frame, xname
# -------------------------------- ver 240512 -------------------------------- #
# TaskQue
from Qutils.logger_custom import CustomLog

from typing import Callable, Literal
import asyncio, logging, traceback


    

class Taskq:

    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'async')
        
        self._queue = asyncio.Queue()
        # self._task = {}

        self._frame = '<taskq>'

        self._is_all_done = True

    # def set_task(self, async_def: Callable, fname: str = None, msg=False):
    #     if fname is None : fname = async_def.__name__ 
    #     self._task[fname] = async_def
    #     if msg: self._custom.info.msg('set_task', fname, frame=self._frame)

    # ------------------------------------------------------------------------ #
    #                                   async                                  #
    # ------------------------------------------------------------------------ #
    # -------------------------------- enqueue ------------------------------- #
    async def xput_queue(self, fname:str, args:tuple=(), kwargs:dict=None, 
                      timeout:int=None, retry:int=0, msg=False):
        """enqueue fname, args, kwargs"""
        item = (fname, args, kwargs, timeout, retry)
        await self._queue.put(item)
        if msg: self._custom.info.msg('xput_que', fname, f"{args}", frame=self._frame)


    # -------------------------------- dequeue ------------------------------- #
    async def xget_queue(self, msg=False):
        fname, args, kwargs, timeout, retry = await self._queue.get()
        if msg : self._custom.info.msg('xget_que',fname, f"{args}",frame=self._frame)
        return (fname, args, kwargs, timeout, retry)

    # -------------------------------- execute ------------------------------- #
    async def xrun_queue(self,tasks:dict, item:tuple, msg=False):
        """with timeout"""        
        fname, args, kwargs, timeout, retry = item
        if kwargs is None : kwargs = {}
        # if not self._task:
        #     print(f"\033[31m [Warning in 'xexecute()'] tasks has not been set! \033[0m")

        try:
            if msg : self._custom.info.msg('xrun_que', fname, f"{args}",frame=self._frame)
            await asyncio.wait_for(tasks[fname](*args, **kwargs), timeout=timeout)
            
        except Exception as e:
            self._custom.warning.msg('except', fname, f"{args}", e.__class__.__name__,frame=self._frame)
            # print(str(e))
            # traceback.print_exc()

            if retry < 3:
                await self.xput_queue(fname, args, kwargs, timeout, retry+1, msg=False)
                self._custom.warning.msg('retry',fname, f"{args}", f"retry({retry+1})", frame=self._frame)
            else:
                self._custom.error.msg('fail',fname, f"{args}", f"retry({retry})", frame=self._frame)
        finally:
            self._queue.task_done()

    def task_done(self):
        self._queue.task_done()

    def is_tasks_start(self):
        if self._queue._unfinished_tasks != 0 and self._is_all_done:
            self._is_all_done = False
            return 1
        else:
            return 0
    def is_tasks_finish(self):
        if self._queue._unfinished_tasks == 0 and not self._is_all_done:
            self._is_all_done = True
            return 1
        else:
            return 0

# ---------------------------------------------------------------------------- #
#                               named singletone                               #
# ---------------------------------------------------------------------------- #
class TaskQue(Taskq):

    _instances = {}

    def __new__(cls, name:str, *args, **kwargs):
        if name not in cls._instances:
            instance = super(TaskQue, cls).__new__(cls)
            cls._instances[name] = instance
            instance._initialized = False
        return cls._instances[name]

    def __init__(self, name:str='taskq', msg:bool=False):
        if not self._initialized:
            try:
                from Qlogger import Logger
                logger = Logger(name, 'head')
            except ModuleNotFoundError as e:
                logger = None

            self._name = name
            self._custom = CustomLog(logger,'async')
            if msg: self._custom.info.msg('TaskQue')

            self._queue = asyncio.Queue()
            self._task = {}
            self._frame = f"<{name}>"
            self._is_all_done = True
            self._initialized = True


if __name__ == "__main__":

    async def myfun(a,b,c):
        print('start')
        await asyncio.sleep(3)
        print('end')

    async def main():
        # from Qtask.utils.logger_color import ColorLog
        # logger = ColorLog('test','green')
        from Qlogger import Logger
        logger = Logger('task', 'head')
        taskq = Taskq(logger)
        # taskq.set_task(myfun,msg=True)

        tasks = {}
        tasks['myfun'] =  myfun
        # ------------------------------- done ------------------------------- #
        # await taskq.xenqueue('myfun', (1,2),{'c':3},timeout=5,msg=True)
        # item = await taskq.xdequeue(msg=True)
        # await taskq.xexecute(item,msg=True)

        # ------------------------------- retry ------------------------------ #
        await taskq.xput_queue('myfun', (1,2),{'c':3},timeout=2,msg=True)
        item = await taskq.xget_queue(msg=True)
        await taskq.xrun_queue(tasks, item,msg=True)
        item = await taskq.xget_queue(msg=True)
        await taskq.xrun_queue(tasks,item,msg=True)
        item = await taskq.xget_queue(msg=True)
        await taskq.xrun_queue(tasks,item,msg=True)
        item = await taskq.xget_queue(msg=True)
        await taskq.xrun_queue(tasks,item,msg=True)


    asyncio.run(main())

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()