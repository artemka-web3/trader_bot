from cloudpayments import CloudPayments
from aiodb import BotDB
from aiocloudpayments import AioCpClient
from datetime import datetime, timedelta
import pytz
import asyncio
from db_import import db

"""
v1 - 
pk_a1c3fd07cc4bc56f277ce4ac3f8ed
8d3a80672a4985f41060018f3be3ed33

v2
pk_c8695290fec5bcb40f468cca846d2
d3119d06f156dad88a2ed516957b065b
"""




async def if_sub_didnt_end(user_id):
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
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
                await client.disconnect()
                return True
        elif sub.interval == 'Year' and sub.period == 2:
            cond = False
            if sub.last_transaction_date  is not None:
                cond = bool(datetime.now(tz=pytz.timezone("UTC")) + timedelta(days=180) < sub_last_trx_datetime)
            if sub.status == 'Cancelled' and datetime.now(tz=pytz.timezone("UTC")) < sub_start_datetime or cond:
                await client.disconnect()
                return True
        elif sub.interval == 'Year' and sub.period == 1:
            cond =  False
            if sub.last_transaction_date  is not None:
                cond = bool(datetime.now(tz=pytz.timezone("UTC")) + timedelta(days=365) < sub_last_trx_datetime)
            if sub.status == 'Cancelled' and datetime.now(tz=pytz.timezone("UTC")) < sub_start_datetime or cond:
                await client.disconnect()
                return True
    return False

async def before_end_of_free_sub(user_id):
    await db.connect()
    free_sub = await db.get_free_sub_end(user_id)
    if free_sub is not None:
        free_sub = datetime.strptime(free_sub,  '%Y-%m-%d %H:%M:%S.%f')
        if free_sub > datetime.now():
            await db.close()
            return free_sub - datetime.now()

async def do_have_free_sub(user_id):
    await db.connect()
    free_sub = await db.get_free_sub_end(user_id)
    if free_sub is not None:
        free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
        if free_sub > datetime.now():
            await db.close()
            return True
        else:
            await db.close()
            return False
    await db.close()
    return False

async def get_users_with_free_sub():
    await db.connect()
    all_users = await db.get_all_users()
    if all_users:
        free_users = []
        for user in all_users:
            free_sub = await db.get_free_sub_end(user[0])
            if free_sub:
                free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
                if free_sub > datetime.now() and user[0] not in free_users:
                    free_users.append(user[0])
        return free_users
    await db.close()
    return []


# get subed users id
async def get_subed_users():
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    await db.connect()
    all_users = await db.get_all_users()
    await db.close()
    subed_users = []
    if all_users:
        for user in all_users:
            for sub in await client.find_subscriptions(user[0]):
                if sub.status == 'Active' and user[0] not in subed_users:
                    subed_users.append(user[0])
                elif await if_sub_didnt_end(user[0]) and user[0] not in subed_users:
                    subed_users.append(user[0])
        await client.disconnect()
        return subed_users
    await client.disconnect()
    return []

async def get_unsubed_users():
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    await db.connect()
    all_user_ids = await db.get_all_users()
    unsubed_users = []
    if all_user_ids:
        for user in all_user_ids:
            for sub in await client.find_subscriptions(user[0]):
                if sub.status == 'Cancelled' and user[0] not in unsubed_users and not await if_sub_didnt_end(user[0]):
                    unsubed_users.append(user[0])
        await client.disconnect()
        return unsubed_users
    await client.disconnect()
    await db.close()
    return []

# у чела одна подписка, мы работаем с ней
async def is_in_pay_sys(user_id):
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    subs = []
    for sub in await client.find_subscriptions(user_id):
        subs.append(user_id)
    await client.disconnect()
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
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    for sub in await client.find_subscriptions(str(user_id)):
        sub_start_datetime = datetime.combine(sub.start_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
        if sub.status == 'Active' and sub.successful_transactions_number > 0:
            await client.disconnect()
            return str(sub_start_datetime - datetime.now(tz=pytz.timezone('UTC')))
        elif sub.status == 'Active' and sub.successful_transactions_number == 0:
            left_days = str(sub_start_datetime - datetime.now(tz=pytz.timezone('UTC'))).split(',')[0]
            await client.disconnect()
            return left_days.split(' ')[0]
        elif await if_sub_didnt_end(user_id):
            sub_start_datetime = 0
            sub_last_trx_datetime = 0
            if sub.start_date is not None and sub.last_transaction_date is None:
                sub_start_datetime = datetime.combine(sub.start_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
                left_days = str(sub_start_datetime - datetime.now(tz=pytz.timezone('UTC'))).split(',')[0]
                await client.disconnect()
                return left_days.split(' ')[0]
            elif sub.last_transaction_date is not None:
                sub_last_trx_datetime = datetime.combine(sub.last_transaction_date, datetime.min.time(), tzinfo=pytz.timezone("UTC"))
                left_days = str(sub_last_trx_datetime - datetime.now(tz=pytz.timezone('UTC'))).split(',')[0]
                await client.disconnect()
                return left_days.split(' ')[0]
    await client.disconnect()
    return False

async def count_money_attracted_by_one(user_id):
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    await db.connect()
    money_paid = 0
    for sub in await client.find_subscriptions(str(user_id)):
        if sub.status == 'Active' and sub.successful_transactions_number > 0:
            # get sub price
            money_paid = sub.amount * sub.successful_transactions_number
            await db.update_money_paid(user_id, money_paid)
            break
        # elif sub.status == 'Active' and sub.successful_transactions_number == 0:
        #     money_paid = sub.amount
        #     db.update_money_paid(user_id, money_paid)
        #     break
    await client.disconnect()
    await db.close()
    return money_paid

async def count_money_attracted_by_ref(ref_id):
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    db.connect()
    users = await db.get_ref_users(ref_id)
    money_paid = 0
    for user in users:
        for sub in await client.find_subscriptions(str(user[0])):
            if sub.status == 'Active' and sub.successful_transactions_number > 0:
                # get sub price
                money_paid += sub.amount * sub.successful_transactions_number
                await db.update_money_paid(user[0], sub.amount * sub.successful_transactions_number)
                break
            # elif sub.status == 'Active' and sub.successful_transactions_number == 0:
            #     money_paid += sub.amount
            #     db.update_money_paid(user[0], sub.amount)
            #     break
    await client.disconnect()
    await db.close()
    return money_paid
async def cancel_sub(user_id):
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    for sub in await client.find_subscriptions(str(user_id)):
        if sub.status == 'Active':
            await client.cancel_subscription(sub.id)
    await client.disconnect()

async def update_sub(user_id, days):
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
    for sub in await client.find_subscriptions(str(user_id)):
        if sub.status == 'Active':
            start_date = sub.start_date
            cancel_sub(user_id)
            await client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days))
            await client.disconnect()
            return True
    await client.disconnect()
    return False


async def update_sub_for_all(days):
    client = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')

    await db.connect()
    all_users = await db.get_all_users()
    if all_users:
        for user in all_users:
            for sub in await client.find_subscriptions(str(user[0])):
                if sub.status == 'Active' and not do_have_free_sub(user[0]):
                    await client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days))
    await client.disconnect()
    await db.close()

# async def main():
#     client_demo = AioCpClient('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
#     subs = await client_demo.find_subscriptions(764315256)
#     for i in await client_demo.find_subscriptions(764315256):
#         print(i.account_id)
#     await client_demo.disconnect()
              
# loop = asyncio.get_event_loop()
# print(loop.run_until_complete(get_subed_users()))