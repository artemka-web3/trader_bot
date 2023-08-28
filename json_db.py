import json 
import aiofiles
import asyncio
from datetime import datetime


file_lock = asyncio.Lock()

"""
[
    {
        id: 0,
        user_id: 11111111,
        referer_id: 22222222,
        money_paid: 0,
        trxId: 000000,
        is_partner: 0,
        free_sub_end: 2023-08-15
    }
]
"""

async def load_data_from_db():
    async with file_lock:
        try:
            async with aiofiles.open('db.json', mode="r", encoding='utf-8') as f:
                return json.loads(await f.read().replace("'", '"').replace(']]', ']').replace('[[', '['))
        except json.JSONDecodeError:
            return []
        except FileNotFoundError:
            return []
        

async def save_data_to_db(data):
    async with file_lock:
        async with aiofiles.open('db.json', 'w', encoding='utf-8') as file:
            await file.write(json.dumps(data, indent=4))

async def add_user(user_id, referer_id=None, money_paid=0, trxId=None, is_partner=0, free_sub_end=None):
    new_id = 0
    data = await load_data_from_db()
    if data:
        new_id = data[-1]['id'] + 1
    new_item = {
        "id": new_id,
        "user_id": user_id,
        "referer_id": referer_id,
        "money_paid": money_paid,
        "trxId": trxId,
        "is_partner": is_partner,
        "free_sub_end": free_sub_end
    }
    data.append(new_item)
    await save_data_to_db(data)

async def if_user_exists(user_id):
    data = await load_data_from_db()
    is_user_exists = any(item['user_id'] == user_id for item in data)
    return is_user_exists

async def get_all_users():
    data = await load_data_from_db()
    user_ids = [(item['user_id'],) for item in data]
    return user_ids

async def is_partner(user_id):
    data = await load_data_from_db()
    for item in data:
        if item['user_id'] == user_id:
            if item['is_partner'] == 1:
                return True
            else:
                return False

async def set_partner(user_id):
    data = await load_data_from_db()
    for item in data:
        if item['user_id'] == user_id:
            item['is_partner'] = 1
            break
    await save_data_to_db(data)

async def get_free_sub_end(user_id):
    data = await load_data_from_db()
    for item in data:
        if item['user_id'] == user_id:
            return item['free_sub_end']
        
async def set_free_sub_end(user_id, timestamp):
    data = await load_data_from_db()
    for item in data:
        if item['user_id'] == user_id:
            item['free_sub_end'] = timestamp
    await save_data_to_db(data)

async def get_referer_traffic(referer_id):
    data = await load_data_from_db()
    user_ids = [(item['user_id'],) for item in data if item['referer_id'] == referer_id]
    return len(user_ids)

async def get_ref_users(referer_id):
    data = await load_data_from_db()
    user_ids = [(item['user_id'],) for item in data if item['referer_id'] == referer_id]
    return user_ids

async def update_money_paid(user_id, money_paid):
    data = await load_data_from_db()
    for item in data:
        if item['user_id'] == user_id:
            item['money_paid'] += money_paid
            break
    await save_data_to_db(data)

async def get_money_paid_by_user(user_id):
    data = await load_data_from_db()
    for item in data:
        if item['user_id'] == user_id:
            return item['money_paid']

async def get_money_amount_attracted_by_referer(referer_id):
    data = await load_data_from_db()
    total_money_paid = 0
    for item in data:
        if item['referer_id'] == referer_id:
            total_money_paid += item['money_paid']
    return total_money_paid

def convert_strdate_to_date(strdate):
    date_object = datetime.strptime(strdate, "%Y-%m-%d")
    return date_object
    

#  - - - - - - - TEST - - - - - - - -
# async def main():
#     await user_exists(111111111)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())