from Qperiodic.utils.logger_custom import CustomLog
from Qperiodic.job import Job
from Qperiodic.tools.timer import Timer
import logging
from typing import Literal,Coroutine
import signal


class Periodic:

    def __init__(self, logger:logging.Logger = None):
        self.logger = logger
        self.timer = Timer(self.logger)
        self.job = Job(self.logger)

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

    def job_register(self, coro:Coroutine, fname:str=None):
        self.job.register(coro, fname)

    def producer(self):
        pass
        
    def consumer(self):
        pass



if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test', 'head')
    periodic = Periodic(logger)
    periodic.timer.run_daemon_thread()
    periodic.job_register()
    