from Qperiodic.utils.log_custom import CustomLog
from Qperiodic.job import Job
from Qperiodic.tools.timer import Timer
from logging import Logger
from typing import Literal,Coroutine
import signal




class Periodic:


    def __init__(self, value:float, unit:Literal['second','minute','hour'], logger:Logger = None):
        self.log = logger
        self.job = Job(self.log)

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()


    def job_register(self, coro:Coroutine, fname:str=None):
        self.job.register(coro, fname)

    def producer(self )