from aiogram import types

keyb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
buttons = ['Купить Подписку', 'Подписка']
keyb.add(*buttons)