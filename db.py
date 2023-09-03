import aiosqlite
import asyncio
from cloudpayments import CloudPayments
from datetime import datetime, timedelta
import datetime as dt


client = CloudPayments('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
offset = dt.timezone(timedelta(hours=3))

def convert_strdate_to_date(strdate):
    try:
        date_object = datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S.%f")
    except:
        date_object = datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S%z")
    return date_object

"""
BASIC OPERATIONS –– BASIC OPERATIONS –– BASIC OPERATIONS –– BASIC OPERATIONS –– BASIC OPERATIONS ––
"""
async def if_user_exists(user_id):
    try:
        async with aiosqlite.connect('db.db') as conn:
            async with conn.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,)) as cursor:
                return bool(len(await cursor.fetchall()))
    except aiosqlite.Error as e:
        print(f"Error executing query: {e}")
        return []

async def add_user(user_id, referer_id=None):
    try:
        if referer_id != None:
            async with aiosqlite.connect('db.db') as conn:
                async with conn.execute("INSERT INTO `users` (`user_id`, `referer_id`) VALUES (?, ?)", (user_id, referer_id,)) as cursor:
                    await conn.commit()
        else:
            async with aiosqlite.connect('db.db') as conn:
                async with conn.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,)) as cursor:
                    await conn.commit()
    except aiosqlite.Error as e:
        print(f"Error executing query: {e}")
        return []
    
async def get_all_users():
    try:
        async with aiosqlite.connect('db.db') as conn:
            async with conn.execute("SELECT user_id FROM `users`") as cursor:
                return await cursor.fetchall()
    except aiosqlite.Error as e:
        print(f"Error executing query: {e}")
        return []
    





"""
PARTNERSHIP THINGS –– PARTNERSHIP THINGS –– PARTNERSHIP THINGS –– PARTNERSHIP THINGS –– PARTNERSHIP THINGS
"""    
async def is_partner(user_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT is_partner FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row[0]) if row else False

async def set_partner(user_id):
    async with aiosqlite.connect('db.db') as conn:
        await conn.execute('UPDATE users SET is_partner = 1 WHERE user_id = ?', (user_id,))
        await conn.commit()

async def del_partner(user_id):
    async with aiosqlite.connect('db.db') as conn:
        await conn.execute('UPDATE users SET is_partner = 0 WHERE user_id = ?', (user_id,))
        await conn.commit()






 

"""
FREESUB -– FREESUB -–  FREESUB -– FREESUB -– FREESUB -– FREESUB -– FREESUB -– FREESUB -– FREESUB
"""
async def get_free_sub_end(user_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT free_sub_end FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def before_end_of_free_sub(user_id):
    free_sub = await get_free_sub_end(user_id)
    if free_sub is not None:
        free_sub = convert_strdate_to_date(free_sub)
        if free_sub > datetime.now(offset):
            return (free_sub - datetime.now(offset)).days
        
async def do_have_free_sub(user_id):
    free_sub = await get_free_sub_end(user_id)
    if free_sub is not None:
        free_sub = convert_strdate_to_date(free_sub)
        if free_sub > datetime.now(offset):
            return True
        else:
            return False
    return False

async def set_free_sub_end(user_id, timestamp):
    async with aiosqlite.connect('db.db') as conn:
        await conn.execute('UPDATE users SET free_sub_end = ? WHERE user_id = ?', (timestamp, user_id,))
        await conn.commit()









"""
PAIDSUB -– PAIDSUB -–  PAIDSUB -– PAIDSUB -– PAIDSUB -– PAIDSUB -– PAIDSUB -– PAIDSUB -– PAIDSUB
"""
async def get_paid_sub_end(user_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT paid_sub_end FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def before_end_of_paid_sub(user_id):
    paid_sub = await get_paid_sub_end(user_id)
    if paid_sub is not None:
        paid_sub = convert_strdate_to_date(paid_sub)
        if paid_sub > datetime.now(offset):
            return (paid_sub - datetime.now(offset)).days
        
async def do_have_paid_sub(user_id):
    paid_sub = await get_paid_sub_end(user_id)
    if paid_sub is not None:
        paid_sub = convert_strdate_to_date(paid_sub)
        if paid_sub > datetime.now(offset):
            return True
        else:
            return False
    return False

async def set_paid_sub_end(user_id, timestamp):
    async with aiosqlite.connect('db.db') as conn:
        await conn.execute('UPDATE users SET paid_sub_end = ? WHERE user_id = ?', (timestamp, user_id,))
        await conn.commit()

async def is_in_payment_system(user_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT in_payment_system FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row[0])

async def update_sub(user_id, days):
    for sub in client.list_subscriptions(user_id):
        if sub.status == 'Active':
            client.cancel_subscription(user_id)
            await client.update_subscription(sub.id, start_date=datetime.now(offset)+timedelta(days=days+1))
            await set_paid_sub_end(user_id, datetime.now(offset)+timedelta(days=days+1))

            

async def update_sub_for_all(days):
    all_users = await get_users_with_paid_sub_only()
    for user in all_users:
        for sub in client.list_subscriptions(str(user)):
            if sub.status == 'Active':
                client.cancel_subscription(sub.id)
                client.update_subscription(sub.id, start_date=datetime.now(offset)+timedelta(days=days+1))
                await set_paid_sub_end(user, datetime.now(offset)+timedelta(days=days+1))





"""
SUB_OPTIMIZE –– SUB_OPTIMIZE –– SUB_OPTIMIZE –– SUB_OPTIMIZE –– SUB_OPTIMIZE –– SUB_OPTIMIZE –– SUB_OPTIMIZE
"""
# check for free sub and for paid sub
async def check_if_subed(user_id):
    if do_have_paid_sub(user_id) or do_have_free_sub(user_id):
        return True
    return False
# users with free sub and with paid sub
async def get_subed_users():
    all_users = await get_all_users()
    subed_users = []
    if all_users:
        for user in all_users:
            if await do_have_paid_sub(user[0]) and user[0] not in subed_users:
                subed_users.append(user[0])
            elif await do_have_free_sub(user[0]) and user[0] not in subed_users:
                subed_users.append(user[0])
        return subed_users
    else:
        return []
async def get_users_with_paid_sub_only():
    all_users = await get_all_users()
    subed_users = []
    if all_users:
        for user in all_users:
            if await do_have_paid_sub(user[0]) and user[0] not in subed_users and not await do_have_free_sub(user[0]):
                subed_users.append(user[0])
        return subed_users
    else:
        return []

async def get_users_with_free_sub_only():
    all_users = await get_all_users()
    subed_users = []
    if all_users:
        for user in all_users:
            if await do_have_free_sub(user[0]) and user[0] not in subed_users and not await do_have_paid_sub(user[0]):
                subed_users.append(user[0])
        return subed_users
    else:
        return []














"""
REFERAL THINGS –– REFERAL THINGS –– REFERAL THINGS –– REFERAL THINGS –– REFERAL THINGS –– REFERAL THINGS
"""
async def get_referer_traffic(referer_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT COUNT(*) FROM users WHERE referer_id = ?', (referer_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0]

async def get_ref_users(referer_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT user_id FROM users WHERE referer_id = ?', (referer_id,)) as cursor:
            return await cursor.fetchall()
    
async def get_money_amount_attracted_by_referer(referer_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT SUM(money_paid) FROM users WHERE referer_id = ?', (referer_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0











"""
MONEY PAID –– MONEY PAID –– MONEY PAID –– MONEY PAID –– MONEY PAID –– MONEY PAID ––
"""
async def update_money_paid(user_id, money_paid):
    async with aiosqlite.connect('db.db') as conn:
        await conn.execute('UPDATE users SET money_paid = money_paid + ? WHERE user_id = ?', (money_paid, user_id))
        await conn.commit()

async def get_money_paid_by_user(user_id):
    async with aiosqlite.connect('db.db') as conn:
        async with conn.execute('SELECT money_paid FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None



# # Main function to run the asynchronous code
# async def main():
#     await add_user(11111111111111)
#     return await get_all_users()
#     Call other functions as needed

# if __name__ == "__main__":
# loop = asyncio.get_event_loop()
# print(loop.run_until_complete(main()))