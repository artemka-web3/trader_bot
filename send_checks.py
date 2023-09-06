from datetime import datetime
from cloudpayments import CloudPayments
from aiocloudpayments import AioCpClient
import logging
import asyncio
import requests

LOGIN = 'KDeOYMPCsp'
PASSWORD = 'cgdCYjFcOSWJYHW'
GROUP_CODE = '9fab4def-2fed-4b05-8b31-a23a3904b043'

client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
logging.basicConfig(level=logging.INFO)

async def send_check_to_all():
    current_date = datetime.now()
    timezone = 'MSK'
    payments = await client.list_payments(current_date, timezone)
    logging.info("send checks")
    if payments:
        for item in payments:
            print(item)
            if "в радаре биржи" not in item.description.lower():
                email_for_check = item.email
                account_id = item.account_id
                terminal_url = item.terminal_url
                pay_state = item.status.lower()
                paymentAmount = item.payment_amount
                description = item.description
                try:
                    check_token = await get_check_token()
                    if pay_state == 'completed':
                        await generate_check(account_id, email_for_check, check_token, paymentAmount, terminal_url, description)
                except Exception as e:
                    logging.info(e)
                await asyncio.sleep(2)
                # отправить
    logging.info("all checks were sent!")

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

# current_date = datetime.now()
# timezone = 'MSK'
# payments = client.list_payments(current_date, timezone)
# for p in payments:
#     print(p.email)

loop = asyncio.get_event_loop()
loop.run_until_complete(send_check_to_all())