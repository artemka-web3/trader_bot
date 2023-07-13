import requests as re
import pandas as pd
from datetime import datetime, timedelta
import datetime as dt
import time

offset = dt.timezone(timedelta(hours=3))

# Login details
login = 'kazakovoleg797@gmail.com'
password = "Inkgroup12!"
s = re.Session()
s.get('https://passport.moex.com/authenticate', auth=(login, password))
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}

# GET ONE STOCK DATA
def fetch_stock(url):
    response = re.get(url, headers=headers, cookies=cookies)
    return response.json()

def one_stock(url):
    data = fetch_stock(url)
    return [
        data['securities']['data'][0][0],  # SECID
        data['securities']['data'][0][9],  # SEC NAME
        data['securities']['data'][0][4],  # LOTSIZE
        data['marketdata']['data'][0][14],  # DAY CHANGE %
    ]

def get_stock_data(security):
    url_get_sec = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}.json"
    return one_stock(url_get_sec)

# PRICE CHANGE
def get_price_change(security):
    current_candle = get_current_stock_volume(security)
    prev_candle = get_prevmin_stock_price(security)
    if prev_candle == -200 or current_candle == -200:
        raise Exception(f"\n{current_candle}\n{prev_candle}\nPRICE CHANGE COUNTING ERROR")
    current_close = current_candle[1]
    prev_close = prev_candle[1]
    return round((float(current_close) * 100 / float(prev_close)) - 100, 3)

# GET ALL MINUTE VOLUMES WITHIN PAST 7 DAYS
def fetch_prev(url):
    response = re.get(url, headers=headers, cookies=cookies)
    return response.json()

def get_prev(url):
    return fetch_prev(url)

volumes_dict = {}    
def get_prev_avg_volume():
    secs = get_securities()
    for sec in secs:
        current_date = datetime.now(offset)
        volumes = []
        current_data = get_current_stock_volume(sec[0])
        empty_days_counter = 0
        if current_data == -200:
            volumes_dict[f'{sec[0]}'] = -200
            break
        else:
            counter = 1
            while counter < 8:
                start = 1
                prev_date = current_date - timedelta(days=counter + empty_days_counter)
                prev_date_str = str(prev_date.strftime('%Y-%m-%d'))
                url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_date_str}&till={prev_date_str}&interval=1&start={start-1}"
                prev_data = get_prev(url)
                if len(prev_data['candles']['data']) == 0:
                    empty_days_counter += 1
                else:
                    while True:
                        if len(prev_data['candles']['data']) == 0:
                            break
                        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_date_str}&till={prev_date_str}&interval=1&start={start-1}"
                        prev_data = get_prev(url)
                        try:
                            volumes.append(float(prev_data['candles']['data'][0][4]))
                            print(prev_data['candles']['data'][0][4])
                            print(start-1)
                            print(prev_date_str)
                            time.sleep(0.2)
                        except:
                            break
                        start += 1
                    counter += 1
            volumes_dict[f'{sec[0]}'] = sum(volumes) / start
    return volumes_dict

# GET CURRENT STOCK VOLUME
def fetch_current_volume(url):
    response = re.get(url, headers=headers, cookies=cookies)
    return response.json()

def get_current_volume(url):
    return fetch_current_volume(url)

def get_current_stock_volume(security):
    current_date = datetime.now(offset) - timedelta(seconds=60)
    cur_time = ("0" + str(current_date.hour) if len(str(current_date.hour)) < 2 else str(current_date.hour)) + ":" + (
            "0" + str(current_date.minute) if len(str(current_date.minute)) < 2 else str(current_date.minute))
    today = current_date.strftime('%Y-%m-%d')
    start_from_for_today = 0
    while True:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        cur_data = get_current_volume(url)
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        cur_data = get_current_volume(url)
        if len(cur_data['candles']['data']) == 0:
            return -200
        else:
            for candle_data in cur_data['candles']['data']:
                if cur_time in candle_data[6]:
                    print("CUR: ", candle_data)
                    return candle_data
                else:
                    start_from_for_today += 1

# GET PREVIOUS MINUTE TIME
def fetch_prevmin_price(url):
    response = re.get(url, headers=headers, cookies=cookies)
    return response.json()

def get_prevmin_price(url):
    return fetch_prevmin_price(url)

def get_prevmin_stock_price(security):
    prevmin_date = datetime.now(offset) - timedelta(seconds=120)
    prevmin_time = ("0" + str(prevmin_date.hour) if len(str(prevmin_date.hour)) < 2 else str(prevmin_date.hour)) + ":" + (
            "0" + str(prevmin_date.minute) if len(str(prevmin_date.minute)) < 2 else str(prevmin_date.minute))
    today = prevmin_date.strftime('%Y-%m-%d')
    start_from_for_today = 0
    while True:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        prev_minute_data = get_prevmin_price(url)
        if len(prev_minute_data['candles']['data']) == 0:
            return -200
        else:
            for candle_data in prev_minute_data['candles']['data']:
                if prevmin_time in candle_data[6]:
                    print("PREV: ", candle_data)
                    return candle_data
                else:
                    start_from_for_today += 1

# GET ALL SECURITIES
def fetch_all_securities(url):
    response = re.get(url, headers=headers, cookies=cookies)
    return response.json()

def all_securities(url):
    data = fetch_all_securities(url)
    return data['securities']['data']

def all_marketdata(url):
    data = fetch_all_securities(url)
    return data['marketdata']['data']

url_get_secs = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
def get_securities():
    return all_securities(url_get_secs)

def get_marketdata():
    return all_marketdata(url_get_secs)

# BUYERS VS. SELLERS
def buyers_vs_sellers1(security):
    current_date = datetime.now(offset)
    today = current_date.strftime('%Y-%m-%d')
    url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=10'
    response = re.get(url)
    data = response.json()['candles']['data']
    columns = response.json()['candles']['columns']
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

with open('file.txt', 'w') as file:
    secs = get_securities()
    for sec in secs:
        file.write(f'{sec[9]}\n')