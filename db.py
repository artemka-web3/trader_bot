import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def add_user(self, user_id, referer_id=None):
        """Добавляем юзера в базу"""
        if referer_id != None:
            self.cursor.execute("INSERT INTO `users` (`user_id`, `referer_id`) VALUES (?, ?)", (user_id, referer_id,))
        else:
            self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
            return self.conn.commit()
    
    def get_all_users(self):
        # всех
        result = self.cursor.execute("SELECT * FROM `users`")
        return [result.fetchall()[0][1]]

    def is_partner(self, user_id):
        result = self.cursor.execute("SELECT is_partner FROM `users` WHERE user_id = ?", (user_id,))
        return bool(result.fetchone()[0] == 1)
    
    def set_partner(self, user_id):
        self.cursor.execute("UPDATE users SET is_partner = ? WHERE user_id = ?", (1, user_id,))
        return self.conn.commit()

    def get_free_sub_end(self, user_id):
        result = self.cursor.execute("SELECT free_sub_end FROM `users` WHERE user_id = ?", (user_id,))
        return result.fetchone()[0]

    def set_free_sub_end(self, user_id, timestamp):
        self.cursor.execute("UPDATE users SET free_sub_end = ? WHERE user_id = ?", (timestamp, user_id,))
        return self.conn.commit()

    def get_referer_traffic(self, referer_id):
        result = self.cursor.execute("SELECT COUNT(*) FROM users WHERE referer_id = ?", (referer_id,))
        return result.fetchone()[0]
    
    def update_money_paid(self, user_id, money_paid):
        self.cursor.execute("UPDATE users SET money_paid = ? WHERE user_id = ?", (money_paid, user_id,))
        return self.conn.commit()

    def get_money_paid_by_user(self, user_id):
        result = self.cursor.execute("SELECT `money_paid` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_money_amount_attracted_by_referer(self, referer_id):
        result = self.cursor.execute("SELECT SUM(money_paid) FROM users WHERE referer_id = ?", (referer_id,))
        return self.cursor.fetchone()[0]

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()

