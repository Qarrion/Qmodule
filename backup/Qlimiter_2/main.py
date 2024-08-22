from Qlimiter import Rate
from Qlimiter.modules import pool

rate = Limiter.Rate()

pool = Limiter.Pool()


rate.limiter
pool.wait_for_result
pool.fire_and_forget


from Qlimiter import Limiter


Limiter