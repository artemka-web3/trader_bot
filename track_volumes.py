import threading
import time
import logging
from moex_sync import *
from volumes_json_sync import  *
from datetime import datetime

logging.basicConfig(level=logging.INFO)


threads = []
tasks = []

def collect_stocks():
    global tasks
    securities = get_securities()
    with open('shares_v2.csv', mode='r') as reader:
        for row in reader:
            if row is not None:
                for stock in securities:
                    if row.split(',')[1] == stock[0]:
                        print(stock[0])
                        coef = int(row.split(',')[-1])
                        tasks.append([stock, coef])
    # fill threads

    for task in tasks:
        thread = threading.Thread(target=share_thread, args=(task[0], task[1],))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)

def share_thread(stock, coef):
    while True:
        if datetime.now().hour < 24 and datetime.now().hour > 10 and datetime.now().weekday() < 6:
            tracked_volumes = read_json()
            volume_avg_prev = read_json_file()
            if volume_avg_prev != {}:
                try:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    current_hour = ("0" + str(datetime.now().hour) if len(str(datetime.now().hour)) < 2 else str(datetime.now().hour))
                    current_minute = ("0" + str(datetime.now().minute-1) if len(str(datetime.now().minute-1)) < 2 else str(datetime.now().minute - 1))
                    current_time = str(current_hour) + ":" + str(current_minute)
                    stock_data = get_stock_data(stock[0])
                    current_stock_data = get_current_stock_volume(stock[0], current_time)
                    price_change = get_price_change(current_stock_data[0], current_stock_data[1])
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
                    buyers_sellers = buyers_vs_sellers1(price_change_status)
                    buyers = buyers_sellers[0]  # %
                    sellers = buyers_sellers[1]  # %
                    dir = '🔵'
                    if price_change > 0:
                        dir = "🟢"
                    elif price_change < 0:
                        dir = "🔴"
                    check_volume = volume_avg_prev[stock[0]]
                    #print(f"{stock[0]} volume: {volume_rub} coef: {coef} check_volume: {check_volume} result: {bool(coef*check_volume<volume_rub)}")
                    #logging.info(f"{stock[0]} volume: {volume_rub} coef: {coef} check_volume: {check_volume} result: {bool(coef*check_volume<volume_rub)}")
                    if check_volume * coef < volume_rub and volume_rub > 1000000:
                        #print('Повышенные ', stock[0])
                        logging.info(f'Повышенные {stock[0]}')
                        data = {
                            "sec_id": sec_id,
                            "sec_name": sec_name,
                            "day_change": day_change,
                            "current_price": current_price,
                            "volume_rub": volume_rub,
                            "lot_amount": lot_amount,
                            "price_change": price_change,
                            "buyers": buyers,
                            "sellers": sellers,
                            "dir": dir,
                            "time": current_time,
                            'current_date': current_date
                        }
                        tracked_volumes.append(data)
                        write_json(tracked_volumes)
                    #else
                        #print('Пропуск ', stock[0])
                except Exception as e:
                    logging.info(f'{stock[0]}: {e}')
        time.sleep(60)

collect_stocks()
for thread in threads:
    thread.join()

