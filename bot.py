import telebot
import time
from telebot import types
from config import API_TOKEN


bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вы нажали start")

if __name__ == '__main__':
    bot.polling(none_stop=True)