import asyncio, time, traceback

class Blocking:

    async def worker(self,xcontext=None,msg_run=False,msg_close=False,msg_limit=False):
        task_name = asyncio.current_task().get_name()
        while True:
            item = await self._queue.get()
            async with self._semaphore:
                #! ------------------------------------------------------------ #
                # print(f"[i n] balancer({self._name}), remain({self._semaphore._value}/{self._n_worker})")
                #! ------------------------------------------------------------ #
                self._is_empty = False # for manager
                # ----------------------------- close ---------------------------- #
                if item is None:
                    self._queue.task_done()
                    if msg_close:self._custom.info.msg('close',widths=(3,),aligns=("^"),paddings=("."))
                    break
                # ---------------------------- process --------------------------- #
                else:
                    try:
                        tsp_start = time.time()  #! limiter
                        kwargs=dict() if item.kwargs is None else item.kwargs
                        if msg_run:self._custom.info.msg(item.name, self._xcontext_type, str(item.args))
                        
                        if xcontext is None:
                            result = await asyncio.wait_for(self._xtask[item.name](*item.args, **kwargs),50)
                        else:
                            result = await asyncio.wait_for(self._xtask[item.name](xcontext, *item.args, **kwargs),50)
                        item.future.set_result(result)  
                        
                    except asyncio.exceptions.CancelledError as e:
                        cprint(f" - worker ({task_name}) closed",'yellow')

                    except Exception as e:
                        if item.retry < self._n_retry:
                            # ---------------------------------------------------- #
                            # print(self._s_reset*(item.retry+1)/(self._n_retry*5))
                            # ---------------------------------------------------- #
                            buffer = round(self._s_reset*(item.retry/self._n_retry),3)
                            await asyncio.sleep(buffer)
                            await self._xput_queue_retry(item=item)
                            self._custom.warning.msg(item.name, f'retry({item.retry+ 1})',f"buff({buffer})")
                        else:
                            self._custom.error.msg(item.name,'drop', str(item.args))
                            if self._traceback: traceback.print_exc()

                            #! for break execute
                            item.future.set_result(e) 
                            raise e
                            # traceback.print_exc()
                    finally:
                        if self._limit : 
                            tsp_finish = time.time() #! limiter
                            await self._wait_reset(tsp_start, tsp_finish, msg_limit=msg_limit)
                        self._queue.task_done()