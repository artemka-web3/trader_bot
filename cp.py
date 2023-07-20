import cloudpayments
from db import BotDB
from datetime import datetime, timedelta
import pytz

db = BotDB('prod.db')
client = cloudpayments.CloudPayments('pk_a1c3fd07cc4bc56f277ce4ac3f8ed', '8d3a80672a4985f41060018f3be3ed33')

def check_if_user_in_payment_system(user_id):
    subs = []
    for i in client.list_subscriptions(str(user_id)):
        subs.append(i)
    return len(subs) == 0
        

# check if subed
def check_if_subed(user_id):
    for sub in client.list_subscriptions(str(user_id)):
        if sub.status == 'Cancelled':
            if sub.interval == 'Month':
                if sub.start_date.month + 1 > datetime.now().month:
                    return True
            elif sub.interval == 'SemiYear':
                if sub.start_date.month + 6 > datetime.now().month:
                    return True
            elif sub.interval == 'Year':
                if sub.start_date.year + 1 > datetime.now().year:
                    return True
        elif sub.status == 'Active':
            return True
    return False

def check_if_active(user_id):
    for sub in client.list_subscriptions(str(user_id)):
        if sub.status == 'Active':
            return True
    return False

# get subed users id
def get_subed_users():
    all_user_ids = db.get_all_users()
    subed_users = []
    for user_id in all_user_ids:
        for sub in client.list_subscriptions(str(user_id)):
            if sub.status == 'Cancelled':
                if sub.interval == 'Month':
                    if sub.start_date.month + 1 > datetime.now().month:
                        subed_users.append(user_id)
                elif sub.interval == 'Year' and sub.period == 2:
                    if sub.start_date.month + 6 > datetime.now().month:
                        subed_users.append(user_id)
                elif sub.interval == 'Year' and sub.period == 1:
                    if sub.start_date.year + 1 > datetime.now().year:
                        subed_users.append(user_id)
            elif sub.status == 'Active':
                subed_users.append(user_id)
    for user_id in all_user_ids:
        if user_id not in subed_users:
            check_free_sub = db.get_free_sub_end(user_id)
            now_time = datetime.now(tz=pytz.timezone('Europe/Moscow'))
            if check_free_sub > now_time:
                subed_users.append(user_id)
    return subed_users

def get_unsubed_users():
    all_user_ids = db.get_all_users()
    unsubed_users = []
    for user_id in all_user_ids:
        for sub in client.list_subscriptions(str(user_id)):
            if sub.status == 'Cancelled':
                unsubed_users.append(user_id)
    for user_id in all_user_ids:
        if db.get_money_paid_by_user(user_id) == 0:
            if not user_id in unsubed_users:
                unsubed_users.append(user_id)
    for user_id in all_user_ids:
        if user_id not in unsubed_users:
            check_free_sub = db.get_free_sub_end(user_id)
            now_time = datetime.now(tz=pytz.timezone('Europe/Moscow'))  
            if check_free_sub < now_time:
                unsubed_users.append(user_id)
    return unsubed_users

# get_sub_end == get_next_trx_date
def get_sub_end(user_id):
    for sub in client.list_subscriptions(str(user_id)):
        if sub.status == 'Active' and sub.successful_transactions_number > 0:
            return str(sub.start_date - datetime.now(tz=pytz.timezone('UTC')))
        elif sub.status == 'Active' and sub.successful_transactions_number == 0:
            left_days = str(sub.start_date - datetime.now(tz=pytz.timezone('UTC'))).split(',')[0]
            return left_days.split(' ')[0]
    return False

def count_money_attracted_by_one(user_id):
    money_paid = 0
    for sub in client.list_subscriptions(str(user_id)):
        if sub.status == 'Active' and sub.successful_transactions_number > 0:
            # get sub price
            money_paid = sub.amount * sub.successful_transactions_number
            db.update_money_paid(user_id, money_paid)
        elif sub.status == 'Active' and sub.successful_transactions_number == 0:
            money_paid = sub.amount
            db.update_money_paid(user_id, money_paid)
    return money_paid

def cancel_sub(user_id):
    for sub in client.list_subscriptions(str(user_id)):
        if sub.status == 'Active':
            client.cancel_subscription(sub.id)

def update_sub(user_id, days):
    for sub in client.list_subscriptions(str(user_id)):
        if sub.status == 'Active':
            start_date = sub.start_date
            client.update_subscription(sub.id, start_date=start_date+timedelta(days=days))

def update_sub_for_all(days):
    all_users = db.get_all_users()
    for user in all_users:
        for sub in client.list_subscriptions(str(user)):
            if sub.status == 'Active':
                start_date = sub.start_date
                client.update_subscription(sub.id, start_date=start_date+timedelta(days=days))

            

 