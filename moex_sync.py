import pandas as pd
import requests as re
from datetime import datetime, timedelta
import datetime as dt
import time
import logging
import csv
import requests

offset = dt.timezone(timedelta(hours=3))

#login – email, указанный при регистрации на сайте moex.com
login = 'kazakovoleg797@gmail.com'
#password – пароль от учетной записи на сайте moex.com
password = "Inkgroup12!"
s = re.Session()
s.get('https://passport.moex.com/authenticate', auth=(login, password))
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
s.close()

def get_value_by_ticker(ticker):
    with open('shares.csv', 'r') as reader:
        for row in csv.DictReader(reader, delimiter='\n'):
            # Обработка словаря данных
            if row is not None:
                if row['Полное название акций ,тикет,сокращённое название '] is not None:
                    if row['Полное название акций ,тикет,сокращённое название '].split(',')[1] == ticker:
                        return row['Полное название акций ,тикет,сокращённое название '].split(',')[2] 

def fetch_stock(session, url, headers, cookies):
    with session.get(url, headers=headers, cookies=cookies) as response:
        return response.json()

def one_stock(url, headers, cookies):
    with requests.Session() as session:
        data = fetch_stock(session, url, headers, cookies)
        name = get_value_by_ticker(data['securities']['data'][0][0])
        return (
            data['securities']['data'][0][0], # SECID, 
            str(name), # SECNAME
            data['securities']['data'][0][4], # LOTSIZE
            data['marketdata']['data'][0][20], # DAY CHANGE %
        )

def get_stock_data(security):
    url_get_sec = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}.json"
    return one_stock(url_get_sec, headers, cookies)

url_get_secs = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
def fetch_all_securities(session, url, headers, cookies):
    with session.get(url, headers=headers, cookies=cookies) as response:
        return response.json()

def all_securities(url, headers, cookies):
    with requests.Session() as session:
        data = fetch_all_securities(session, url, headers, cookies)
        return data['securities']['data']

def all_marketdata(url, headers, cookies):
    with requests.Session() as session:
        data = fetch_all_securities(session, url, headers, cookies)
        return data['marketdata']['data']

def get_securities():
    return all_securities(url_get_secs, headers, cookies)

def get_marketdata():
    return all_marketdata(url_get_secs, headers, cookies)

def fetch_current_volume(session, url, headers, cookies):
    with session.get(url, headers=headers, cookies=cookies) as response:
        return response.json()

def get_current_volume(url, headers, cookies):
    with requests.Session() as session:
        data = fetch_current_volume(session, url, headers, cookies)
        return data

def get_current_stock_volume(security):
    login = 'kazakovoleg797@gmail.com'
    #password – пароль от учетной записи на сайте moex.com
    password = "Inkgroup12!"
    s = re.Session()
    s.get('https://passport.moex.com/authenticate', auth=(login, password))
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
    cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
    s.close()
    current_date = datetime.now(offset) # - timedelta(hours=10)
    cur_time = ("0" +str(current_date.hour) if len(str(current_date.hour)) < 2 else str(current_date.hour)) + ":" + ("0" +str(current_date.minute) if len(str(current_date.minute)) < 2 else str(current_date.minute))
    today = current_date.strftime('%Y-%m-%d')
    start_from_for_today = 0
    while True:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        cur_data= get_current_volume(url, headers, cookies)
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        cur_data = get_current_volume(url, headers, cookies)
        if len(cur_data['candles']['data']) == 0:
            return -200
        else: 
            for candle_data in cur_data['candles']['data']:
                if cur_time in candle_data[6]:
                    print("CUR: ", candle_data)
                    return candle_data
                else:
                    start_from_for_today += 1

def fetch_prevmin_price(session, url, headers, cookies):
    with session.get(url, headers=headers, cookies=cookies) as response:
        return response.json()

def get_prevmin_price(url, headers, cookies):
    with requests.Session() as session:
        data = fetch_prevmin_price(session, url, headers, cookies)
        return data

def get_prevmin_stock_price(security):
    login = 'kazakovoleg797@gmail.com'
    #password – пароль от учетной записи на сайте moex.com
    password = "Inkgroup12!"
    s = re.Session()
    s.get('https://passport.moex.com/authenticate', auth=(login, password))
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
    cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
    s.close()
    prevmin_date = datetime.now(offset) - timedelta(minutes=1) # - timedelta(hours=10)
    prevmin_time = ("0" +str(prevmin_date.hour) if len(str(prevmin_date.hour)) < 2 else str(prevmin_date.hour)) + ":" + ("0" +str(prevmin_date.minute) if len(str(prevmin_date.minute)) < 2 else str(prevmin_date.minute))
    today = prevmin_date.strftime('%Y-%m-%d')
    start_from_for_today = 0
    while True:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        prev_minute_data= get_prevmin_price(url, headers, cookies)
        if len(prev_minute_data['candles']['data']) == 0:
            return -200
        else: 
            for candle_data in prev_minute_data['candles']['data']:
                if prevmin_time in candle_data[6]:
                    print("PREV: ", candle_data)
                    return candle_data
                else:
                    start_from_for_today += 1

def get_price_change(security):
    current_candle = get_current_stock_volume(security)
    prev_candle = get_prevmin_stock_price(security)
    if prev_candle == -200 or current_candle == -200:
        raise Exception(f"\n{current_candle}\n{prev_candle}\nPRICE CHANGE COUNTING ERROR")
    current_close = current_candle[1]
    prev_close = prev_candle[1]
    #return current_candle, current_close, current_close, prev_close
    return round((float(current_close) * 100 / float(prev_close)) - 100, 2)

def fetch_prev(session, url, headers, cookies):
    with session.get(url, headers=headers, cookies=cookies) as response:
        return response.json()

def get_prev(url, headers, cookies):
    with requests.Session() as session:
        data = fetch_prev(session, url, headers, cookies)
        return data

def get_prev_avg_volume(volumes_dict):
    secs = get_securities()
    for sec in secs:
        counter = 1
        empty_days = 0
        minutes = 0
        value = 0
        print(sec[0])
        volumes_dict[sec[0]] = 0
        while counter < 8:
            prev_date = (datetime.now(offset)- timedelta(days=counter)).strftime('%Y-%m-%d') # - timedelta(hours=10)
            url_hour = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_date}&till={prev_date}&interval=60&start=0"
            prev_data_hour = get_prev(url_hour, headers, cookies)
            if len(prev_data_hour['candles']['data']) != 0:  
                url_day = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_date}&till={prev_date}&interval=24&start=0"
                prev_data_day = get_prev(url_day, headers, cookies)
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

def fetch_bs(session, url, headers, cookies):
    with session.get(url, headers=headers, cookies=cookies) as response:
        return response.json()

def get_bs(url, headers, cookies):
    with requests.Session() as session:
        data = fetch_bs(session, url, headers, cookies)
        return data

def buyers_vs_sellers1(security):
    current_date = datetime.now(offset) # for test: - timedelta(days=1)
    today = current_date.strftime('%Y-%m-%d')
    url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1'
    response = get_bs(url, headers, cookies)
    data = response['candles']['data']
    columns = response['candles']['columns']
    df = pd.DataFrame(data, columns=columns)
    buyers = len(df[df['close'] > df['open']])
    sellers = len(df[df['close'] < df['open']])

    total = buyers + sellers
    if total > 0:
        buyers = round(buyers / total * 100)
        sellers = round(sellers / total * 100)
    else:
        buyers = 0
        sellers = 0

    return buyers, sellers
