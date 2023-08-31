import json
import asyncio
import aiosqlite
from datetime import datetime


async def if_user_exists(user_id):
    try:
        async with aiosqlite.connect('prod.sqlite3') as conn:
            async with conn.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,)) as cursor:
                return bool(len(await cursor.fetchall()))
    except aiosqlite.Error as e:
        print(f"Error executing query: {e}")
        return []
async def add_user(user_id, referer_id=None):
    try:
        if referer_id != None:
            async with aiosqlite.connect('prod.sqlite3') as conn:
                async with conn.execute("INSERT INTO `users` (`user_id`, `referer_id`) VALUES (?, ?)", (user_id, referer_id,)) as cursor:
                    await conn.commit()
        else:
            async with aiosqlite.connect('prod.sqlite3') as conn:
                async with conn.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,)) as cursor:
                    await conn.commit()
    except aiosqlite.Error as e:
        print(f"Error executing query: {e}")
        return []
    
async def get_all_users():
    try:
        async with aiosqlite.connect('prod.sqlite3') as conn:
            async with conn.execute("SELECT user_id FROM `users`") as cursor:
                return await cursor.fetchall()
    except aiosqlite.Error as e:
        print(f"Error executing query: {e}")
        return []
    
async def is_partner(user_id):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        async with conn.execute('SELECT is_partner FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row[0]) if row else False

async def set_partner(user_id):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        await conn.execute('UPDATE users SET is_partner = 1 WHERE user_id = ?', (user_id,))
        await conn.commit()

async def get_free_sub_end(user_id):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        async with conn.execute('SELECT free_sub_end FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_free_sub_end(user_id, timestamp):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        await conn.execute('UPDATE users SET free_sub_end = ? WHERE user_id = ?', (timestamp, user_id))
        await conn.commit()

async def get_referer_traffic(referer_id):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        async with conn.execute('SELECT COUNT(*) FROM users WHERE referer_id = ?', (referer_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0]

async def get_ref_users(referer_id):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        async with conn.execute('SELECT user_id FROM users WHERE referer_id = ?', (referer_id,)) as cursor:
            return await cursor.fetchall()

async def update_money_paid(user_id, money_paid):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        await conn.execute('UPDATE users SET money_paid = money_paid + ? WHERE user_id = ?', (money_paid, user_id))
        await conn.commit()

async def get_money_paid_by_user(user_id):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        async with conn.execute('SELECT money_paid FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_money_amount_attracted_by_referer(referer_id):
    async with aiosqlite.connect('prod.sqlite3') as conn:
        async with conn.execute('SELECT SUM(money_paid) FROM users WHERE referer_id = ?', (referer_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

def convert_strdate_to_date(strdate):
    date_object = datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S.%f")
    return date_object

# # Main function to run the asynchronous code
# async def main():
#     await add_user(11111111111111)
#     return await get_all_users()
#     Call other functions as needed

# if __name__ == "__main__":
# loop = asyncio.get_event_loop()
# print(loop.run_until_complete(main()))
