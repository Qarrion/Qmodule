import asyncio
from re import T
from Qprocon.tools.nowst import Nowst
from Qprocon.modules.producer import Core

# ---------------------------------------------------------------------------- #
from datetime import datetime, timedelta

nowst = Nowst()
nowst.set_core(Core, msg=True)

# nowst.now_stamp(msg=True)
# nowst.now_naive(msg=True)
# nowst.now_kst(msg=True)1

# # nowst.fetch_offset(msg=True, msg_debug=True)
# # nowst.fetch_offset(msg=True)
# # nowst.sync_offset()
# print(Core.buffer)

async def main():
    await nowst.xsync_offset(msg=True)
    tgt = nowst.now_kst(msg=True) + timedelta(seconds=10)
    # await nowst.xadjust(tgt)

asyncio.run(main())
# ---------------------------------------------------------------------------- #


from Qprocon.tools.timer import Timer
timer = Timer()

timer.set_core(Core, msg=True)

timer.minute_at_seconds(10,'KST')
print(timer.hour_at_minutes(10,'KST'))

# timer.day_at_hours(10,'KST')