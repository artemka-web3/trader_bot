from datetime import datetime, timedelta
from cloudpayments import CloudPayments
from aiocloudpayments import AioCpClient
from send_check_json import *
import logging
import asyncio
import requests

LOGIN = 'KDeOYMPCsp'
PASSWORD = 'cgdCYjFcOSWJYHW'
GROUP_CODE = '9fab4def-2fed-4b05-8b31-a23a3904b043'

client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
client1 = CloudPayments('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')

logging.basicConfig(level=logging.INFO)

async def collect_payments_task():
    current_date = datetime.now()
    timezone = 'MSK'
    payments = await client.list_payments(current_date, timezone)
    data = await read_trxs()
    for p in payments:
        if "в радаре биржи" not in p.description.lower() and p.status == 'Completed':
            existing_trx_ids = [item["trx_id"] for item in data]
            if p.transaction_id not in existing_trx_ids:
                note = {"check": False, "trx_id": p.transaction_id, "terminal_url": p.terminal_url, "email": p.email, "amount": p.payment_amount, "description": p.description, "account_id": p.account_id}
                data.append(note)
                await write_trxs(data)

async def send_checks_task():
    data = await read_trxs()
    await clear_trxs()
    if data:
        for item in data:
            if not item['check']:
                try:
                    token = await get_check_token()
                    await generate_check(item['account_id'], item['email'], token, item['amount'], item['terminal_url'], item['description'])
                    item['check'] = True
                    await write_trxs(data)
                except Exception as e:
                    logging.info(e)
        logging.info('check were sent!')



async def clearing():
    await clear_trxs()

async def get_check_token():
    requestData = {
        "login": LOGIN,
        "pass": PASSWORD,
    }

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    response = requests.post(
        'https://fiscalization.evotor.ru/possystem/v5/getToken',
        json=requestData,
        headers=headers
    )
    return response.json()['token']

async def generate_check(account_id, email, token_evotor, amount, terminal_url, desc):
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day
    hours = current_date.hour
    minutes = current_date.minute
    seconds = current_date.second

    formatted_date = f"{day:02d}.{month:02d}.{year} {hours:02d}:{minutes:02d}:{seconds:02d}"
    timestamp_in_seconds = int(current_date.timestamp())

    api_url = 'https://fiscalization.evotor.ru/possystem/v5'
    group_code = GROUP_CODE
    option = 'sell'
    token_ev = token_evotor
    url_with_params = f"{api_url}/{group_code}/{option}?token={token_ev}"

    receipt_data = {
        "timestamp": formatted_date,
        "external_id": f"{account_id}{timestamp_in_seconds}",
        "receipt": {
            "client": {
                "email": f"{email}",
            },
            "company": {
                "email": "romanovcapi@gmail.com",
                "sno": "usn_income",
                "inn": "434586393116",
                "payment_address": f'{terminal_url}'
            },
            "items": [
                {
                    "name": f"{desc}",
                    "price": int(amount),
                    "quantity": 1.0,
                    "measure": 0,
                    "sum": int(amount),
                    "payment_method": "full_payment",
                    "payment_object": 4,
                    "vat": {
                        "type": "none"
                    }
                }
            ],
            "payments": [
                {
                    "type": 2,
                    "sum": int(amount)
                }
            ],
            "total": int(amount)
        }
    }

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(url_with_params, json=receipt_data, headers=headers)

    if response.status_code == 200:
        logging.info("Success!")
        # Add your redirection logic here
    else:
        logging.info("Error:", response.text)

async def checks_task():
    await collect_payments_task()
    await asyncio.sleep(60)
    await send_checks_task()

async def main():
    current_date = datetime.now()
    timezone = 'MSK'
    payments = await client.list_payments(current_date, timezone)
    for p in payments:
        print(p)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())