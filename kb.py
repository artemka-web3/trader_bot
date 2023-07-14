from aiogram import types

# keyboard for users who don't have subscription
keyb_for_unsubed = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
keyb_for_unsubed.add(types.KeyboardButton(text="Купить подписку")) 
keyb_for_unsubed.add(types.KeyboardButton(text="Пользовательское соглашение"))

# keyboard for users who have subscription
keyb_for_subed = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
keyb_for_subed.add(types.KeyboardButton(text="О боте. Руководство")) 
keyb_for_subed.add(types.KeyboardButton(text="Подписка")) 
keyb_for_subed.add(types.KeyboardButton(text="Пользовательское соглашение"))



