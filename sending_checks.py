import aioschedule
from aiocp import send_check_to_all
import asyncio

def schedule_tasks():
    aioschedule.every().day.at('23:50').do(send_check_to_all)


async def main():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

asyncio.run(main())