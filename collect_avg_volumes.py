from moex_async import cookies, headers, get_securities
import aiohttp
import datetime as dt
from datetime import datetime, timedelta
import asyncio
from volumes_json import *
import logging

logging.basicConfig(level=logging.INFO)
offset = dt.timezone(timedelta(hours=3))



async def collecting_avg():
    await clear_json_file()
    logging.info('started collecting average volumes')
    secs = await get_securities()
    prev_volumes = await read_json_file()
    for sec in secs:
        prev_volumes[sec[0]] = 0
        minutes = 0
        prev_month = (datetime.now(offset)- timedelta(days=31*3)) # получается первое месяца  число в любом случае
        prev_month_start = (prev_month - timedelta(days=prev_month.day)).strftime("%Y-%m-%d")
        current_date = datetime.now(offset).strftime('%Y-%m-%d')
        # месяц текущий будет последни, он нам не нужен: берем 1,он второй; берем 2, он 3-ий; берем 3 - он 4-ый
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_month_start}&till={current_date}&interval=31"
        try:
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.get(url, headers=headers, cookies=cookies) as response:
                    data = await response.json()
                    if len(data['candles']['data']) != 0:
                        for i in data['candles']['data'][0:3]:
                            if '30' in i[-1][8:10]:
                                minutes = 43200
                                prev_volumes[sec[0]] += round(i[4]/minutes, 3)
                            elif '31' in i[-1][8:10]:
                                minutes = 44640
                                prev_volumes[sec[0]] += round(i[4]/minutes, 3)
                            elif '28' in i[-1][8:10]:
                                minutes = 40320
                                prev_volumes[sec[0]] += round(i[4]/minutes, 3)
                            elif '29' in i[-1][8:10]:
                                minutes = 41760
                                prev_volumes[sec[0]] += round(i[4]/minutes, 3)
                    print(prev_volumes[sec[0]])
                    await asyncio.sleep(.2)
        except Exception as e:
            print(e)
            await asyncio.sleep(.1)
    logging.info('average volumes collected')
    await write_json_file(prev_volumes)

loop = asyncio.get_event_loop()
loop.run_until_complete(collecting_avg())

