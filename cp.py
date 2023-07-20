import cloudpayments
from db import BotDB
from datetime import datetime, timedelta
import pytz

"""
v1 - 
pk_a1c3fd07cc4bc56f277ce4ac3f8ed
8d3a80672a4985f41060018f3be3ed33

v2
pk_c8695290fec5bcb40f468cca846d2
d3119d06f156dad88a2ed516957b065b
"""

db = BotDB('prod.db')
client = cloudpayments.CloudPayments('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')

def do_have_free_sub(user_id):
    free_sub = db.get_free_sub_end(user_id)
    if free_sub is not None:
        free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
        if free_sub > datetime.now():
            return True
        else:
            return False
    return False

def get_users_with_free_sub():
    try:
        all_users = db.get_all_users()
        if all_users:
            free_users = []
            for user in all_users:
                free_sub = db.get_free_sub_end(user)
                if free_sub:
                    free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
                    if free_sub > datetime.now() and user not in free_users:
                        free_users.append(user)
            return free_users
        return []
    except Exception as e:
        print(e)


# get subed users id
def get_subed_users():
    all_users = db.get_all_users()
    subed_users = []
    if all_users:
        for user in all_users:
            for sub in client.list_subscriptions(user[0]):
                if sub.status == 'Active' and user not in subed_users:
                    subed_users.append(user)
        return subed_users
    return []

def get_unsubed_users():
    all_user_ids = db.get_all_users()
    unsubed_users = []
    if all_user_ids:
        for user in all_user_ids:
            for sub in client.list_subscriptions(user[0]):
                if sub.status == 'Cancelled' and user not in unsubed_users:
                    unsubed_users.append(user)
        return unsubed_users
    return []

# у чела одна подписка, мы работаем с ней
def is_in_pay_sys(user_id):
    subs = []
    for sub in client.list_subscriptions(user_id):
        subs.append(user_id)
    return len(subs)

# check if subed
def check_if_subed(user_id):
    subed_users = get_subed_users()
    if subed_users:
        if user_id in subed_users:
            return True
    return False
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
            client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days))
            return True
    return False

def buy_not_first_time(user_id, days):
    for sub in client.list_subscriptions(str(user_id)):
        if sub.status == 'Cancelled':
            client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days))

def update_sub_for_all(days):
    all_users = db.get_all_users()
    if all_users:
        for user in all_users:
            for sub in client.list_subscriptions(str(user[0])):
                if sub.status == 'Active' and not do_have_free_sub(user):
                    client.update_subscription(sub.id, start_date=datetime.now()+timedelta(days=days))

