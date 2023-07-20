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

# buying keyboard
b_keyb = types.InlineKeyboardMarkup(row_width=1)
b_keyb.add(types.InlineKeyboardButton(text="На 1 месяц", callback_data = "month", url=""))
b_keyb.add(types.InlineKeyboardButton(text="На 6 месяцев", callback_data = "semi_year", url=""))
b_keyb.add(types.InlineKeyboardButton(text="На 1 год", callback_data="year", url=""))

#existing buyer keyboard
ex_b_keyb = types.InlineKeyboardMarkup(row_width=1)
ex_b_keyb.add(types.InlineKeyboardButton(text="На 1 месяц", callback_data = "exb_month", url=""))
ex_b_keyb.add(types.InlineKeyboardButton(text="На 6 месяцев", callback_data = "exb_semi_year", url=""))
ex_b_keyb.add(types.InlineKeyboardButton(text="На 1 год", callback_data="exb_year", url=""))

# cancel keyboard
c_keyb = types.InlineKeyboardMarkup(row_width=1)
c_keyb.add(types.InlineKeyboardButton(text="Отменить подписку", callback_data='cancel_sub'))

# time for sub kb
time_for_sub_keyb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
time_for_sub_keyb.add(types.KeyboardButton(text="1 месяц"))
time_for_sub_keyb.add(types.KeyboardButton(text="6 месяцев"))
time_for_sub_keyb.add(types.KeyboardButton(text="Год"))

# one or multiple users
one_or_m = types.ReplyKeyboardMarkup(resize_keyboard=True , row_width=2)
one_or_m.add(types.KeyboardButton(text="Один"))
one_or_m.add(types.KeyboardButton(text="Несколько"))







