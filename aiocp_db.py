from cloudpayments import CloudPayments
from aiocloudpayments import AioCpClient
from datetime import datetime, timedelta
import pytz
import asyncio
from aiodb import *
import requests
import logging

logging.basicConfig(level=logging.INFO)


"""
v1 - 
pk_a1c3fd07cc4bc56f277ce4ac3f8ed
8d3a80672a4985f41060018f3be3ed33

v2
pk_c8695290fec5bcb40f468cca846d2
d3119d06f156dad88a2ed516957b065b
"""
LOGIN = 'KDeOYMPCsp'
PASSWORD = 'cgdCYjFcOSWJYHW'
GROUP_CODE = '9fab4def-2fed-4b05-8b31-a23a3904b043'
client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')


async def if_sub_didnt_end(user_id):
    for sub in await client.find_subscriptions(str(user_id)): 
        sub_start_datetime = 0
        sub_last_trx_datetime = 0
        if sub.start_date is not None:
            sub_start_datetime = datetime.combine(sub.start_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
        if sub.last_transaction_date is not None:
            sub_last_trx_datetime = datetime.combine(sub.last_transaction_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
        if sub.interval == 'Month': 
            cond = False
            if sub.last_transaction_date is not None:
                cond = bool(datetime.now(tz=pytz.timezone("UTC")) + timedelta(days=30) < sub_last_trx_datetime)
            if sub.status == 'Cancelled' and datetime.now(tz=pytz.timezone("UTC")) < sub_start_datetime or cond:
                return True
        elif sub.interval == 'Year' and sub.period == 2:
            cond = False
            if sub.last_transaction_date  is not None:
                cond = bool(datetime.now(tz=pytz.timezone("UTC")) + timedelta(days=180) < sub_last_trx_datetime)
            if sub.status == 'Cancelled' and datetime.now(tz=pytz.timezone("UTC")) < sub_start_datetime or cond:
                return True
        elif sub.interval == 'Year' and sub.period == 1:
            cond =  False
            if sub.last_transaction_date  is not None:
                cond = bool(datetime.now(tz=pytz.timezone("UTC")) + timedelta(days=365) < sub_last_trx_datetime)
            if sub.status == 'Cancelled' and datetime.now(tz=pytz.timezone("UTC")) < sub_start_datetime or cond:
                return True
    return False

async def before_end_of_free_sub(user_id):
    free_sub = await get_free_sub_end(user_id)
    if free_sub is not None:
        free_sub = convert_strdate_to_date(free_sub)
        if free_sub > datetime.now():
            return free_sub - datetime.now()

async def do_have_free_sub(user_id):
    free_sub = await get_free_sub_end(user_id)
    if free_sub is not None:
        free_sub = convert_strdate_to_date(free_sub)
        if free_sub > datetime.now():
            return True
        else:
            return False
    return False

async def get_users_with_free_sub():
    all_users = await get_all_users()
    if all_users:
        free_users = []
        for user in all_users:
            free_sub = await get_free_sub_end(user[0])
            if free_sub:
                free_sub = convert_strdate_to_date(free_sub)
                if free_sub > datetime.now() and user[0] not in free_users:
                    free_users.append(user[0])
        return free_users
    return []


# get subed users id
async def get_subed_users():
    all_users = await get_all_users()
    subed_users = []
    if all_users:
        for user in all_users:
            for sub in await client.find_subscriptions(user[0]):
                if sub.status == 'Active' and user[0] not in subed_users:
                    subed_users.append(user[0])
                elif await if_sub_didnt_end(user[0]) and user[0] not in subed_users:
                    subed_users.append(user[0])
        return subed_users
    return []

async def get_unsubed_users():
    all_user_ids = await get_all_users()
    unsubed_users = []
    if all_user_ids:
        for user in all_user_ids:
            for sub in await client.find_subscriptions(user[0]):
                if sub.status == 'Cancelled' and user[0] not in unsubed_users and not await if_sub_didnt_end(user[0]):
                    unsubed_users.append(user[0])
        return unsubed_users
    return []

# у чела одна подписка, мы работаем с ней
async def is_in_pay_sys(user_id):
    subs = []
    for sub in await client.find_subscriptions(user_id):
        subs.append(user_id)
    return bool(len(subs)>0)

# check if subed
async def check_if_subed(user_id):
    subed_users = await get_subed_users()
    if subed_users:
        if user_id in subed_users:
            return True
    return False

# get_sub_end == get_next_trx_date
async def get_sub_end(user_id):
    for sub in await client.find_subscriptions(str(user_id)):
        sub_start_datetime = datetime.combine(sub.start_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
        if sub.status == 'Active' and sub.successful_transactions_number > 0:
            return str(sub_start_datetime - datetime.now(tz=pytz.timezone('UTC')))
        elif sub.status == 'Active' and sub.successful_transactions_number == 0:
            left_days = str(sub_start_datetime - datetime.now(tz=pytz.timezone('UTC'))).split(',')[0]
            return left_days.split(' ')[0]
        elif await if_sub_didnt_end(user_id):
            sub_start_datetime = 0
            sub_last_trx_datetime = 0
            if sub.start_date is not None and sub.last_transaction_date is None:
                sub_start_datetime = datetime.combine(sub.start_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
                left_days = str(sub_start_datetime - datetime.now(tz=pytz.timezone('UTC'))).split(',')[0]
                return left_days.split(' ')[0]
            elif sub.last_transaction_date is not None:
                sub_last_trx_datetime = datetime.combine(sub.last_transaction_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
                left_days = str(sub_last_trx_datetime - datetime.now(tz=pytz.timezone('UTC'))).split(',')[0]
                return left_days.split(' ')[0]
    return False

async def count_money_attracted_by_one(user_id):
    money_paid = 0
    for sub in await client.find_subscriptions(str(user_id)):
        if sub.status == 'Active' and sub.successful_transactions_number > 0:
            # get sub price
            money_paid = sub.amount * sub.successful_transactions_number
            await update_money_paid(user_id, money_paid)
            break
        # elif sub.status == 'Active' and sub.successful_transactions_number == 0:
        #     money_paid = sub.amount
        #     db.update_money_paid(user_id, money_paid)
        #     break
    return money_paid

async def count_money_attracted_by_ref(ref_id):
    return await get_money_amount_attracted_by_referer(ref_id)

async def cancel_sub(user_id):
    for sub in await client.find_subscriptions(str(user_id)):
        if sub.status == 'Active':
            await client.cancel_subscription(sub.id)

async def update_sub(user_id, days):
    for sub in await client.find_subscriptions(user_id):
        print(sub)
        if not await check_if_subed(user_id):
            await client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days+1))
        else:
            left_days = await get_sub_end(int(user_id))
            await cancel_sub(user_id)
            print(left_days)
            await client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days+1+int(left_days)))
        return True
    return False


async def update_sub_for_all(days):
    all_users = await get_all_users()
    if all_users:
        for user in all_users:
            for sub in await client.find_subscriptions(str(user[0])):
                if not await check_if_subed(user[0]):
                    await client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days+1))
                else:
                    left_days = await get_sub_end(int(user[0]))
                    await cancel_sub(user[0])
                    print(left_days)
                    await client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days+1+int(left_days)))
"""
ОСУЩЕСТВЛЕНИЕ ОТПРАВКИ ЧЕКОВ По ПЛАТЕЖАМ КОТОРЫЕ ПРОШЛИ НЕ ДЛЯ БОТА
- вызов раз в день с получением тек. даты в таком формате "2014-08-09"
- если слово 'подписка':
    есть: скип
    нет: 
        1) получить email & account_id & статус платежа &  terminal url & paymentAmount
        2) сформировать чек
        3) отправить запрос на формирование чека
        4) отправка
"""
async def send_check_to_all():
    current_date = datetime.now().strftime("%Y-%m-%d")
    timezone = 'MSK'
    payments = await client.list_payments(current_date, timezone)
    logging.info("send checks")
    for item in payments:
        print(item)
        if "подписк" not in item.description.lower():
            email_for_check = item.email
            account_id = item.account_id
            pay_state = item.status.lower()
            terminal_url = item.terminal_url
            paymentAmount = item.payment_amount
            description = item.description
            check_token = await get_check_token()
            if pay_state == 'completed':
                await generate_check(account_id, email_for_check, check_token, paymentAmount, terminal_url, description)
            await asyncio.sleep(2)
            # отправить

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
        print("Success!")
        # Add your redirection logic here
    else:
        print("Error:", response.text)



# async def main():
#     current_date = (datetime.now() -timedelta(days=2)).strftime("%Y-%m-%d")
#     timezone = 'MSK'
#     payments = await client.list_payments(current_date, timezone)
#     print(payments)
#     for sub in await client.find_subscriptions(str(1701759150)):
#         print(sub.status)
#     print(await check_if_subed(1701759150))
#     # print(await is_in_pay_sys(1701759150))
#     #436419688
#     #1701759150
#     # 6554601918
    
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
