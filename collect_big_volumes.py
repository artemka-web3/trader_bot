import asyncio
from datetime import datetime, timedelta
import json
from moex_async import *
from collect_avg_volumes import read_json_file
from volumes_json import  *



async def collect_stocks():
    tasks = []
    securities = await get_securities()

    # check if stock[0] in csv
    async with aiofiles.open('shares_v2.csv', mode='r') as reader:
        async for row in aiocsv.AsyncDictReader(reader, delimiter='\n'):
            if row is not None:
                for stock in securities:
                    if row['Полное название акций,тикет,сокращённое название,ликвидность'] is not None:
                        if row['Полное название акций,тикет,сокращённое название,ликвидность'].split(',')[1] == stock[0]:
                            print(stock[0])
                            coef = int(row['Полное название акций,тикет,сокращённое название,ликвидность'].split(',')[-1])
                            task = track_big_volume(stock, coef)
                            tasks.append(task)
            
        #task = asyncio.create_task(process_stock(stock, volumes_avg_prev))
    for task in tasks:
        asyncio.create_task(task)
        await asyncio.sleep(5)

async def track_big_volume(stock, coef):
    while True:
        volume_avg_prev = await read_json_file()
        tracked_volumes = await read_json()
        if volume_avg_prev != {}:
            try:
                current_date = datetime.now().strftime("%Y-%m-%d")
                current_hour = ("0" +str(datetime.now(offset).hour) if len(str(datetime.now(offset).hour)) < 2 else str(datetime.now(offset).hour))
                current_minute = ("0" +str(datetime.now(offset).minute - 1) if len(str(datetime.now(offset).minute - 1)) < 2 else str(datetime.now(offset).minute - 1))
                current_time = str(current_hour) +":"+ str(current_minute)
                stock_data = await get_stock_data(stock[0])
                current_stock_data = await get_current_stock_volume(stock[0], current_time)
                price_change = await get_price_change(current_stock_data[0], current_stock_data[1])
                sec_id = stock_data[0]
                sec_name = stock_data[1] 
                lot_size = stock_data[2]
                day_change = stock_data[3]
                current_price = current_stock_data[1]
                volume_rub = current_stock_data[4]
                volume_shares = current_stock_data[5] 
                lot_amount = round(volume_shares / lot_size, 2)
                price_change_status = 0
                if price_change > 0:
                    price_change_status = 1
                elif price_change < 0:
                    price_change_status = 2
                buyers_sellers = await buyers_vs_sellers1(price_change_status)
                buyers = buyers_sellers[0] # %
                sellers = buyers_sellers[1] # %
                dir = '🔵'
                if price_change > 0:
                    dir = "🟢"
                elif price_change < 0:
                    dir = "🔴"
                check_volume = volume_avg_prev[stock[0]]
                if check_volume * coef < volume_rub and volume_rub > 1000000:
                    print('Повышенные ',stock[0])
                    data = {"sec_id": sec_id, "sec_name": sec_name, "day_change": day_change, "current_price": current_price, "volume_rub": volume_rub, "lot_amount":lot_amount, "price_change": price_change, "buyers": buyers, "sellers": sellers, "dir": dir, "time": current_time, 'current_date': current_date}
                    tracked_volumes.append(data)
                    await write_json(tracked_volumes)
                else:
                    print('Пропуск ', stock[0])
            except Exception as e:
                print(f'{stock[0]}: {e}')
        await asyncio.sleep(60)

loop = asyncio.get_event_loop()
loop.run_until_complete(collect_stocks())
