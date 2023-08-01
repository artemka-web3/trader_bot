import aiosqlite

class BotDB():
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        self.connection = None
   
    async def connect(self):
        try:
            self.connection = await aiosqlite.connect(self.db_name)
        except aiosqlite.Error as e:
            print(f"Error connecting to the database: {e}")

    async def close(self):
        if self.connection is not None:
            await self.connection.close()

    async def user_exists(self, user_id):
        try:
            async with self.connection.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,)) as cursor:
                return bool(len(await cursor.fetchall()))
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []

    async def add_user(self, user_id, referer_id=None):
        try:
            if referer_id != None:
                async with self.connection.execute("INSERT INTO `users` (`user_id`, `referer_id`) VALUES (?, ?)", (user_id, referer_id,)) as cursor:
                    await self.connection.commit()
            else:
                async with self.connection.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,)) as cursor:
                    await self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    async def get_all_users(self):
        try:
            async with self.connection.execute("SELECT user_id FROM `users`") as cursor:
                return await cursor.fetchall()
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    async def is_partner(self, user_id):
        try:
            async with self.connection.execute("SELECT is_partner FROM `users` WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return bool(result[0] == 1)
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []

    async def set_partner(self, user_id):
        try:
            async with self.connection.execute("UPDATE users SET is_partner = ? WHERE user_id = ?", (1, user_id,)) as cursor:
                return self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []

    async def get_free_sub_end(self, user_id):
        try:
            async with self.connection.execute("SELECT free_sub_end FROM `users` WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0]
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []

    async def set_free_sub_end(self, user_id, timestamp):
        try:
            async with self.connection.execute("UPDATE users SET free_sub_end = ? WHERE user_id = ?", (timestamp, user_id,)) as cursor:
                return self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    async def get_referer_traffic(self, referer_id):
        try:
            async with self.connection.execute("SELECT COUNT(*) FROM users WHERE referer_id = ?", (referer_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0]
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []
    
    async def get_ref_users(self, ref_id):
        try:
            async with self.connection.execute("SELECT user_id FROM users WHERE referer_id = ?", (ref_id,)) as cursor:
                return await cursor.fetchall()
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    async def update_money_paid(self, user_id, money_paid):
        try:
            async with self.connection.execute("UPDATE users SET money_paid = money_paid + ? WHERE user_id = ?", (money_paid, user_id,)) as cursor:
                return self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []

    async def get_money_paid_by_user(self, user_id):
        try:
            async with self.connection.execute("SELECT `money_paid` FROM `users` WHERE `user_id` = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0]
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []

    async def get_money_amount_attracted_by_referer(self, referer_id):
        try:
            async with self.connection.execute("SELECT SUM(money_paid) FROM users WHERE referer_id = ?", (referer_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0]
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return []

