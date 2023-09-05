import aioschedule
import asyncio
from collect_avg_volumes import *
from send_checks import *
from track_subs import *



def schedule_tasks():
    aioschedule.every().day.at("01:00").do(collecting_avg)
    aioschedule.every().day.at('09:00').do(track_all_subs)
    aioschedule.every().day.at('23:30').do(send_check_to_all)


async def main():
    schedule_tasks()
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

asyncio.run(main())