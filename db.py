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
            self.cursor.execute("INSERT INTO `users` (`user_id`, `is_subscribed`, `referer_id`) VALUES (?, ?, ?)", (user_id, 0, referer_id,))
        else:
            self.cursor.execute("INSERT INTO `users` (`user_id`, `is_subscribed`) VALUES (?, ?)", (user_id, 0,))
            return self.conn.commit()

    def unsubcribe(self, user_id):
        # отписка
        self.cursor.execute("UPDATE users SET is_subscribed = 0 WHERE user_id = ?", (user_id,))
        return self.conn.commit()

    def subcribe(self, user_id, sub_end, sub_start):
        # подписка
        self.cursor.execute("UPDATE users SET is_subscribed = 1, sub_start = ?, sub_end = ?, money_paid = money_paid + ? WHERE user_id = ?", (sub_start, sub_end, 500, user_id,))
        return self.conn.commit()
    
    def check_if_subed(self, user_id):
        result = self.cursor.execute("SELECT is_subscribed FROM `users` WHERE user_id = ?", (user_id,))
        return result.fetchone()[0]

    def get_all_users(self):
        # всех
        result = self.cursor.execute("SELECT * FROM `users`")
        return result.fetchall()
    
    def get_subed_users(self):
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `is_subscribed` = 1")
        return result.fetchall() 
    
    def get_unsubed_users(self):
        # получение тех кто не подписан
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `is_subscribed` = 0") 
        return result.fetchall() 
    
    def get_user_id_with_end_timestamp(self):
        #  получение user_id и его конечного срока подписки чтоб вовремя удалять подписчиков
        result = self.cursor.execute("SELECT user_id, sub_end FROM users")
        return result.fetchall()

    def get_referer_traffic(self, referer_id):
        result = self.cursor.execute("SELECT COUNT(*) FROM users WHERE referer_id = ?", (referer_id,))
        return result.fetchone()[0]
    
    def get_money_paid_by_user(self, user_id):
        result = self.cursor.execute("SELECT `money_paid` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_money_amount_attracted_by_referer(self, referer_id):
        result = self.cursor.execute("SELECT SUM(money_paid) FROM users WHERE referer_id = ?", (referer_id,))
        return self.cursor.fetchone()[0]

    def get_sub_end(self, user_id):
        result = self.cursor.execute("SELECT sub_end FROM users WHERE user_id = ?", (user_id,))
        return result.fetchone()[0]


    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()

