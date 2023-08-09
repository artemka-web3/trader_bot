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
login = 'kazakovoleg797@gmail.com'
#password – пароль от учетной записи на сайте moex.com
password = "Inkgroup12!"
s = re.Session()
s.get('http://passport.moex.com/authenticate', auth=(login, password))
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
s.close()

# Create an instance of asyncio event loop
# async def authenticate(login, password):
#     url = "http://passport.moex.com/authenticate"
#     auth = aiohttp.BasicAuth(login, password)
#     headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}

#     async with aiohttp.ClientSession(headers=headers, auth=auth) as session:
#         async with session.get(url) as response:
#             cookies = {'MicexPassportCert': response.cookies['MicexPassportCert']}
#             return cookies
# async def login_moex():
#     login = 'kazakovoleg797@gmail.com'
#     password = "Inkgroup12!"

#     return await authenticate(login, password)
# #login – email, указанный при регистрации на сайте moex.com
# login = 'kazakovoleg797@gmail.com'
# #password – пароль от учетной записи на сайте moex.com
# password = "Inkgroup12!"
# s = re.Session()
# s.get("http://passport.moex.com/authenticate', auth=(login, password))
#headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
# cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
# s.close()
#cookies = 

async def load_csv_data(filename):
    async with aiofiles.open(filename, 'r') as reader:
        data = []
        async for row in aiocsv.AsyncDictReader(reader, delimiter='\n'):
            data.append(row)
        return data

async def get_value_by_ticker(data, ticker):
    for row in data:
        if row is not None:
            parts = row['Полное название акций ,тикет,сокращённое название ,ликвидность'].split(',')
            if len(parts) >= 2 and parts[1] == ticker:
                return parts[2]

async def fetch_stock(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies) as response:
        return await response.json()

async def one_stock(session, data, url, headers, cookies):
    stock_data = await fetch_stock(session, url, headers, cookies)
    ticker = stock_data['securities']['data'][0][0]
    name = await get_value_by_ticker(data, ticker)
    return (
        ticker,
        str(name),
        stock_data['securities']['data'][0][4],
        stock_data['marketdata']['data'][0][25]
    )

async def get_stock_data(security, data, headers, cookies):
    url_get_sec = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}.json"
    async with aiohttp.ClientSession(trust_env=True) as session:
        return await one_stock(session, data, url_get_sec, headers, cookies)

# GET ALL SECURITIES
url_get_secs = "http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"
async def fetch_all_securities(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies) as response:
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
    global cookies
    return await all_securities(url_get_secs, headers, cookies)

async def get_marketdata():
    global cookies
    return await all_marketdata(url_get_secs, headers, cookies)

# TRACK CURRENT VOLUME
async def fetch_current_volume(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies) as response:
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
    global cookies
    while True:
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        cur_data= await get_current_volume(url, headers, cookies)
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

# PRICE CHANGE
async def get_price_change(security, cur_time):
    current_candle = await get_current_stock_volume(security, cur_time)
    #prev_candle = await get_prevmin_stock_price(security)
    #if prev_candle == -200 or current_candle == -200:
    #    raise Exception(f"\n{current_candle}\n{prev_candle}\nPRICE CHANGE COUNTING ERROR")
    if current_candle == -200:
        raise Exception(f"\n{current_candle}\nPRICE CHANGE COUNTING ERROR")
    current_close = current_candle[1]
    current_open = current_candle[0]
    #prev_close = prev_candle[1]
    #return current_candle, current_close, current_close, prev_close
    return round((float(current_close) * 100 / float(current_open)) - 100, 2)


# GET PAST  MONTHS VOLUMES
async def fetch_prev_months(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies) as response:
        return await response.json()

async def get_prev_months(url, headers, cookies):
    async with aiohttp.ClientSession(trust_env=True) as session:
        data = await fetch_prev_months(session, url, headers, cookies)
        return data

async def get_prev_avg_months(volumes_dict, months_to_scroll):
    secs= await get_securities()
    global cookies

    for sec in secs:
        volumes_dict[sec[0]] = 0
        minutes = 0
        prev_month = (datetime.now(offset)- timedelta(days=31*months_to_scroll)) # получается первое месяца  число в любом случае
        prev_month_start = (prev_month - timedelta(days=prev_month.day-1)).strftime("%Y-%m-%d")
        current_date = datetime.now(offset).strftime('%Y-%m-%d')
        # месяц текущий будет последни, он нам не нужен: берем 1,он второй; берем 2, он 3-ий; берем 3 - он 4-ый
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_month_start}&till={current_date}&interval=31"
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
        await asyncio.sleep(.1)
    return volumes_dict


async def get_prev_avg_months_for_table(volumes_dict, months_to_scroll):
    secs= await get_securities()
    global cookies

    for sec in secs:
        volumes_dict[sec[0]] = 0
        minutes = 0
        prev_month = (datetime.now(offset)- timedelta(days=31*months_to_scroll)) # получается первое месяца  число в любом случае
        prev_month_start = (prev_month - timedelta(days=prev_month.day-1)).strftime("%Y-%m-%d")
        current_date = datetime.now(offset).strftime('%Y-%m-%d')
        # месяц текущий будет последни, он нам не нужен: берем 1,он второй; берем 2, он 3-ий; берем 3 - он 4-ый
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_month_start}&till={current_date}&interval=31"
        data = await get_prev_months(url, headers, cookies)
        print(sec[0])
        if len(data['candles']['data']) != 0:
            for i in data['candles']['data'][0:months_to_scroll]:
                if '30' in i[-1][8:10]:
                    minutes = 43200
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4]/minutes, 3), "За 3 месяца": i[4]}
                elif '31' in i[-1][8:10]:
                    minutes = 44640
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4]/minutes, 3), "За 3 месяца": i[4]}
                elif '28' in i[-1][8:10]:
                    minutes = 40320
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4]/minutes, 3), "За 3 месяца": i[4]}
                elif '29' in i[-1][8:10]:
                    minutes = 41760
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4]/minutes, 3), "За 3 месяца": i[4]}
        print(volumes_dict[sec[0]])
        await asyncio.sleep(.1)
    return volumes_dict
    

async def fetch_bs(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies) as response:
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

loop = asyncio.get_event_loop()
print(loop.run_until_complete(get_stock_data('ABRD')))
print(loop.run_until_complete(get_securities()))
print(loop.run_until_complete(get_current_stock_volume('ABRD', '13:47')))