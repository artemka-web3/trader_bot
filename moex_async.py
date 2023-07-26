import aiohttp
import pandas as pd
import asyncio
import requests as re
from datetime import datetime, timedelta
import datetime as dt
import time
import logging
import aiocsv
import aiofiles
import random

offset = dt.timezone(timedelta(hours=3))

# Create an instance of asyncio event loop

#login – email, указанный при регистрации на сайте moex.com
login = 'kazakovoleg797@gmail.com'
#password – пароль от учетной записи на сайте moex.com
password = "Inkgroup12!"
s = re.Session()
s.get('http://passport.moex.com/authenticate', auth=(login, password))
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
s.close()

async def get_value_by_ticker(ticker):
    async with aiofiles.open('shares.csv', 'r') as reader:
        async for row in aiocsv.AsyncDictReader(reader, delimiter='\n'):
            # Обработка словаря данных
            if row is not None:
                if row['Полное название акций ,тикет,сокращённое название '] is not None:
                    if row['Полное название акций ,тикет,сокращённое название '].split(',')[1] == ticker:
                        return row['Полное название акций ,тикет,сокращённое название '].split(',')[2] 

# GET ONE STOCK DATA
async def fetch_stock(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies, ssl=False) as response:
        return await response.json()

async def one_stock(url, headers, cookies):

    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_stock(session, url, headers, cookies)
        name = await get_value_by_ticker(data['securities']['data'][0][0])
        return (
            data['securities']['data'][0][0], # SECID, 
            str(name), # SECNAME
            data['securities']['data'][0][4], # LOTSIZE
            data['marketdata']['data'][0][20], # DAY CHANGE %
        )

    
async def get_stock_data(security):
    url_get_sec = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}.json"
    return await one_stock(url_get_sec, headers, cookies)

# GET ALL SECURITIES
url_get_secs = 'http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
async def fetch_all_securities(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies, ssl=False) as response:
        return await response.json()

async def all_securities(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_all_securities(session, url, headers, cookies)
        return data['securities']['data']
    
async def all_marketdata(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_all_securities(session, url, headers, cookies)
        return data['marketdata']['data']
    
async def get_securities():
    return await all_securities(url_get_secs, headers, cookies)

async def get_marketdata():
    return await all_marketdata(url_get_secs, headers, cookies)

# TRACK CURRENT VOLUME
async def fetch_current_volume(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies, ssl=False) as response:
        return await response.json()

async def get_current_volume(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_current_volume(session, url, headers, cookies)
        return data
    
async def get_current_stock_volume(security, cur_time):
    current_date = datetime.now(offset) # - timedelta(hours=10)
    #cur_time = ("0" +str(current_date.hour) if len(str(current_date.hour)) < 2 else str(current_date.hour)) + ":" + ("0" +str(current_date.minute) if len(str(current_date.minute)) < 2 else str(current_date.minute))
    today = current_date.strftime('%Y-%m-%d')
    start_from_for_today = 0
    while True:
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        cur_data= await get_current_volume(url, headers, cookies)
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        cur_data = await get_current_volume(url, headers, cookies)
        if len(cur_data['candles']['data']) == 0:
            return -200
        else: 
            for candle_data in cur_data['candles']['data']:
                if cur_time in candle_data[6][0:16]:
                    print('CURENT TIME: ', cur_time)
                    print("CUR: ", candle_data)
                    return candle_data
                else:
                    start_from_for_today += 1
# TRACK PREV MINUTE TIME
async def fetch_prevmin_price(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies, ssl=False) as response:
        return await response.json()

async def get_prevmin_price(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_prevmin_price(session, url, headers, cookies)
        return data
    
async def get_prevmin_stock_price(security):
    prevmin_date = datetime.now(offset) - timedelta(minutes=1) # - timedelta(hours=10)
    prevmin_time = ("0" +str(prevmin_date.hour) if len(str(prevmin_date.hour)) < 2 else str(prevmin_date.hour)) + ":" + ("0" +str(prevmin_date.minute) if len(str(prevmin_date.minute)) < 2 else str(prevmin_date.minute))
    today = prevmin_date.strftime('%Y-%m-%d')
    start_from_for_today = 0
    while True:
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        prev_minute_data= await get_prevmin_price(url, headers, cookies)
        if len(prev_minute_data['candles']['data']) == 0:
            return -200
        else: 
            for candle_data in prev_minute_data['candles']['data']:
                if prevmin_time in candle_data[6][0:16]:
                    print("PREV: ", candle_data)
                    return candle_data
                else:
                    start_from_for_today += 1


# PRICE CHANGE
async def get_price_change(security, cur_time):
    current_candle = await get_current_stock_volume(security, cur_time)
    #prev_candle = await get_prevmin_stock_price(security)
    #if prev_candle == -200 or current_candle == -200:
    #    raise Exception(f"\n{current_candle}\n{prev_candle}\nPRICE CHANGE COUNTING ERROR")
    if current_candle == -200:
        raise Exception(f"\n{current_candle}\nPRICE CHANGE COUNTING ERROR")
    current_close = current_candle[1]
    current_open = current_candle[1]
    #prev_close = prev_candle[1]
    #return current_candle, current_close, current_close, prev_close
    return round((float(current_close) * 100 / float(current_open)) - 100, 2)


# GET ALL MINUTE VOLUMES WITHIN PAST 7 DAYS
async def fetch_prev(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies, ssl=False) as response:
        return await response.json()

async def get_prev(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_prev(session, url, headers, cookies)
        return data
    
async def get_prev_avg_volume(volumes_dict):
    secs = await get_securities()
    for sec in secs:
        counter = 1
        empty_days = 0
        minutes = 0
        value = 0
        print(sec[0])
        volumes_dict[sec[0]] = 0
        while counter < 8:
            prev_date = (datetime.now(offset)- timedelta(days=counter)).strftime('%Y-%m-%d') # - timedelta(hours=10)
            url_hour = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_date}&till={prev_date}&interval=60&start=0"
            prev_data_hour = await get_prev(url_hour, headers, cookies)
            if len(prev_data_hour['candles']['data']) != 0:  
                url_day = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_date}&till={prev_date}&interval=24&start=0"
                prev_data_day = await get_prev(url_day, headers, cookies)
                for i in prev_data_day['candles']['data']:
                    if '23:' in i[7]:
                        minutes = 840
                    elif '18:' in i[7]:
                        minutes = 540
                value = prev_data_day['candles']['data'][0][4]
            counter += 1
        if value != 0:
            volumes_dict[sec[0]] += round(value / minutes, 6)
            volumes_dict[sec[0]] = volumes_dict[sec[0]] / (counter - 1)
        else:
            volumes_dict[sec[0]] = f'Ошибка получения данных об акции {sec[0]}'

        print(volumes_dict[sec[0]])
    return volumes_dict

# GET PAST  MONTHS VOLUMES
async def fetch_prev_months(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies, ssl=False) as response:
        return await response.json()

async def get_prev_months(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_prev_months(session, url, headers, cookies)
        return data

async def get_prev_avg_months(volumes_dict, months_to_scroll):
    secs= await get_securities()
    for sec in secs:
        volumes_dict[sec[0]] = 0
        minutes = 0
        prev_month = (datetime.now(offset)- timedelta(days=31*months_to_scroll)) # получается первое месяца  число в любом случае
        prev_month_start = (prev_month - timedelta(days=prev_month.day-1)).strftime("%Y-%m-%d")
        current_date = datetime.now(offset).strftime('%Y-%m-%d')
        # месяц текущий будет последни, он нам не нужен: берем 1,он второй; берем 2, он 3-ий; берем 3 - он 4-ый
        url = f'http ://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_month_start}&till={current_date}&interval=31' 
        data = await get_prev_months(url, headers, cookies)
        print(sec[0])
        if len(data['candles']['data']) != 0:
            for i in data['candles']['data'][0:months_to_scroll]:
                if '30' in i[-1][8:10]:
                    minutes = 43200
                    volumes_dict[sec[0]] += round(i[4]/minutes, 3)
                elif '31' in i[-1][8:10]:
                    minutes = 44640
                    volumes_dict[sec[0]] += round(i[4]/minutes, 3)
                elif '28' in i[-1][8:10]:
                    minutes = 40320
                    volumes_dict[sec[0]] += round(i[4]/minutes, 3)
                elif '29' in i[-1][8:10]:
                    minutes = 41760
                    volumes_dict[sec[0]] += round(i[4]/minutes, 3)
        print(volumes_dict[sec[0]])
    return volumes_dict
    

async def fetch_bs(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies, ssl = False) as response:
        return await response.json()

async def get_bs(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_bs(session, url, headers, cookies)
        return data

async def buyers_vs_sellers1(p_ch_status):
    buyers = 50
    sellers = 50
    if p_ch_status == 1:
        buyers = random.randint(55,100)
        sellers = 100 - buyers
    elif p_ch_status == 2:
        sellers = random.randint(55,100)
        buyers = 100 - sellers

    return buyers, sellers

#loop = asyncio.get_event_loop()
#loop.run_until_complete(get_prevmin_stock_price("SBER"))
