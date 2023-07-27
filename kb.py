from aiogram import types

# keyboard for users who don't have subscription
keyb_for_unsubed = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
keyb_for_unsubed.add(types.KeyboardButton(text="Купить подписку")) 
keyb_for_unsubed.add(types.KeyboardButton(text="Пользовательское соглашение"))

# keyboard for users who have subscription
keyb_for_subed = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
keyb_for_subed.add(types.KeyboardButton(text="О боте. Руководство")) 
keyb_for_subed.add(types.KeyboardButton(text="Подписка")) 

def create_cancel_kb():
    cancel_keyb = types.InlineKeyboardMarkup(row_width=1)
    cancel_keyb.add(types.InlineKeyboardButton(text="Отменить подписку", callback_data='cancel_sub'))
    return cancel_keyb

# buying keyboard
def create_buying_link(user_id):
    b_keyb = types.InlineKeyboardMarkup(row_width=1)
    b_keyb.add(types.InlineKeyboardButton(text="На 1 месяц - 999₽", callback_data = "month", url=f"http://45.9.42.131:3000/month/{user_id}"))
    b_keyb.add(types.InlineKeyboardButton(text="На 6 месяцев - 4999₽", callback_data = "semi_year", url=f"http://45.9.42.131:3000/semi_year/{user_id}"))
    b_keyb.add(types.InlineKeyboardButton(text="На 12 месяцев - 7999₽", callback_data="year", url=f"http://45.9.42.131:3000/year/{user_id}"))
    return b_keyb

#existing buyer keyboard
def create_not_first_time_buying_kb(user_id):
    ex_b_keyb = types.InlineKeyboardMarkup(row_width=1)
    ex_b_keyb.add(types.InlineKeyboardButton(text="На 1 месяц- 999₽", callback_data = "exb_month", url=f"http://45.9.42.131:3000/paymentWidget/{user_id}/999")) # поменять 10 на ориг сумму
    ex_b_keyb.add(types.InlineKeyboardButton(text="На 6 месяцев - 4999₽", callback_data = "exb_semi_year", url=f"http://45.9.42.131:3000/paymentWidget/{user_id}/4999"))
    ex_b_keyb.add(types.InlineKeyboardButton(text="На 12 месяцев - 7999₽", callback_data="exb_year", url=f"http://45.9.42.131:3000/paymentWidget/{user_id}/7999"))
    return ex_b_keyb


# time for sub kb
time_for_sub_keyb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
time_for_sub_keyb.add(types.KeyboardButton(text="1 месяц"))
time_for_sub_keyb.add(types.KeyboardButton(text="6 месяцев"))
time_for_sub_keyb.add(types.KeyboardButton(text="Год"))

# one or multiple users
one_or_m = types.ReplyKeyboardMarkup(resize_keyboard=True , row_width=2)
one_or_m.add(types.KeyboardButton(text="Один"))
one_or_m.add(types.KeyboardButton(text="Несколько"))

# confirm kb
confirm_keyb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
confirm_keyb.add(types.KeyboardButton(text='Да'))
confirm_keyb.add(types.KeyboardButton(text = 'Нет'))








