import requests as re
from datetime import datetime, timedelta
import datetime as dt
import time
import logging
import random
import csv

offset = dt.timezone(timedelta(hours=3))
login = 'kazakovoleg797@gmail.com'
password = "Inkgroup12!"
s = re.Session()
s.get('http://passport.moex.com/authenticate', auth=(login, password))
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
s.close()

def load_csv_data(filename):
    with open(filename, 'r') as reader:
        data = []
        for row in reader:
            data.append(row)
        return data

def get_value_by_ticker(data, ticker):
    for row in data:
        if row is not None:
            parts = row.split(',')
            if len(parts) >= 2 and parts[1] == ticker:
                return parts[2]

def one_stock(data, url, headers, cookies):
    response = re.get(url, headers=headers, cookies=cookies)
    stock_data = response.json()
    ticker = stock_data['securities']['data'][0][0]
    name = get_value_by_ticker(data, ticker)
    return (
        ticker,
        str(name),
        stock_data['securities']['data'][0][4],
        stock_data['marketdata']['data'][0][25]
    )

def get_stock_data(security):
    data = load_csv_data('shares_v2.csv')
    url_get_sec = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}.json"
    return one_stock(data, url_get_sec, headers, cookies)

url_get_secs = "http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"

def all_securities(url, headers, cookies):
    response = re.get(url, headers=headers, cookies=cookies)
    data = response.json()
    return data['securities']['data']

def all_marketdata(url, headers, cookies):
    response = re.get(url, headers=headers, cookies=cookies)
    data = response.json()
    return data['marketdata']['data']

def get_securities():
    return all_securities(url_get_secs, headers, cookies)

def get_marketdata():
    return all_marketdata(url_get_secs, headers, cookies)

def get_current_stock_volume(security, cur_time):
    current_date = datetime.now(offset)
    today = current_date.strftime('%Y-%m-%d')
    start_from_for_today = 0

    while True:
        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?from={today}&till={today}&interval=1&start={start_from_for_today}"
        response = re.get(url, headers=headers, cookies=cookies)
        cur_data = response.json()
        time.sleep(0.5)
        if len(cur_data['candles']['data']) != 0:
            for candle_data in cur_data['candles']['data']:
                if cur_time in candle_data[6][0:16]:
                    return candle_data
                else:
                    start_from_for_today += 1

def get_price_change(open_p, close_p):
    return round(((close_p - open_p) / open_p) * 100, 2)

def get_prev_avg_months(volumes_dict, months_to_scroll):
    secs = get_securities()

    for sec in secs:
        volumes_dict[sec[0]] = 0
        minutes = 0
        prev_month = (datetime.now(offset) - timedelta(days=31 * months_to_scroll))
        prev_month_start = (prev_month - timedelta(days=prev_month.day)).strftime("%Y-%m-%d")
        current_date = datetime.now(offset).strftime('%Y-%m-%d')

        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_month_start}&till={current_date}&interval=31"
        try:
            response = re.get(url, headers=headers, cookies=cookies)
            data = response.json()
            print(sec[0])
            if len(data['candles']['data']) != 0:
                for i in data['candles']['data'][0:months_to_scroll]:
                    if '30' in i[-1][8:10]:
                        minutes = 43200
                        volumes_dict[sec[0]] += round(i[4] / minutes, 3)
                    elif '31' in i[-1][8:10]:
                        minutes = 44640
                        volumes_dict[sec[0]] += round(i[4] / minutes, 3)
                    elif '28' in i[-1][8:10]:
                        minutes = 40320
                        volumes_dict[sec[0]] += round(i[4] / minutes, 3)
                    elif '29' in i[-1][8:10]:
                        minutes = 41760
                        volumes_dict[sec[0]] += round(i[4] / minutes, 3)
                print(volumes_dict[sec[0]])
                time.sleep(.2)
        except Exception as e:
            print(e)
            time.sleep(.2)
    return volumes_dict

def get_prev_avg_months_for_table(volumes_dict, months_to_scroll):
    secs = get_securities()

    for sec in secs:
        volumes_dict[sec[0]] = 0
        minutes = 0
        prev_month = (datetime.now(offset) - timedelta(days=31 * months_to_scroll))
        prev_month_start = (prev_month - timedelta(days=prev_month.day - 1)).strftime("%Y-%m-%d")
        current_date = datetime.now(offset).strftime('%Y-%m-%d')

        url = f"http://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{sec[0]}/candles.json?from={prev_month_start}&till={current_date}&interval=31"
        response = re.get(url, headers=headers, cookies=cookies)
        data = response.json()
        print(sec[0])
        if len(data['candles']['data']) != 0:
            for i in data['candles']['data'][0:months_to_scroll]:
                if '30' in i[-1][8:10]:
                    minutes = 43200
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4] / minutes, 3), "За 3 месяца": i[4]}
                elif '31' in i[-1][8:10]:
                    minutes = 44640
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4] / minutes, 3), "За 3 месяца": i[4]}
                elif '28' in i[-1][8:10]:
                    minutes = 40320
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4] / minutes, 3), "За 3 месяца": i[4]}
                elif '29' in i[-1][8:10]:
                    minutes = 41760
                    volumes_dict[sec[0]] = {'Средние за минуту': round(i[4] / minutes, 3), "За 3 месяца": i[4]}
        print(volumes_dict[sec[0]])
        time.sleep(.1)
    return volumes_dict

def buyers_vs_sellers1(p_ch_status):
    buyers = 50
    sellers = 50
    if p_ch_status == 1:
        buyers = random.randint(55, 100)
        sellers = 100 - buyers
    elif p_ch_status == 2:
        sellers = random.randint(55, 100)
        buyers = 100 - sellers

    return buyers, sellers
