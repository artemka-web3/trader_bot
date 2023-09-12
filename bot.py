"""
IMPORTS –– IMPORTS –– IMPORTS –– IMPORTS –– IMPORTS –– IMPORTS –– IMPORTS
"""
from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
from aiogram.types import ParseMode
from datetime import datetime, timedelta
from config import *
from db import *
from fsm import *
from keyboards import *
from volumes_json import *
from subs_json import *
import datetime as dt
import logging
import aioschedule
import time




"""
CONFIG –– CONFIG –– CONFIG –– CONFIG –– CONFIG –– CONFIG –– CONFIG
"""
logging.basicConfig(level=logging.INFO)
offset = dt.timezone(timedelta(hours=3))
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)














"""
USER HADNLERS –– USER HADNLERS –– USER HADNLERS –– USER HADNLERS –– USER HADNLERS –– USER HADNLERS
"""
@dp.message_handler(lambda message: 'ℹ️ О боте. Руководство' == message.text or message.text.lower() == '/help' or message.text.lower() == '/start')
async def intro(message: types.Message):
    user_exists = await if_user_exists(message.from_user.id)
    if not user_exists:
        start_command = message.text
        referer_id = str(start_command[7:])
        if str(referer_id) != '':
            if str(referer_id) != str(message.from_user.id):
                await add_user(user_id=message.from_user.id, referer_id=int(referer_id))
                try:
                    await bot.send_message(int(referer_id), 'По вашей ссылке зарегался новый юзер', reply_markup=keyb_for_unsubed)
                except:
                    pass
            else:
                await add_user(user_id=message.from_user.id)
                await message.answer("Нельзя регаться по своей же реф. ссылке!", reply_markup=keyb_for_unsubed)
        else:
            await add_user(user_id=message.from_user.id)
    else:
        if await check_if_subed(message.from_user.id):
            with open('intro.jpg', 'rb') as photo:
                await bot.send_photo(message.from_user.id, photo, """<b>"Радар биржи"</b> анализирует все минутные свечи акций торгуемых на Московской бирже. Если бот видит повышенный обьем в акции, то он сразу сигнализирует об этом.\n\n<b>Бот уведомляет:</b>\n\n🔸 Какой обьем был куплен.\n🔸 Изменение цены на данном обьеме.\n🔸 Изменение цены за день.\n🔸 О количестве покупателей и продавцов на данном обьеме.\n\n<b>Этот инструмент должен быть у каждого инвестора!</b>""", reply_markup=keyb_for_subed, parse_mode=ParseMode.HTML)
        else:
            with open('intro.jpg', 'rb') as photo:
                await bot.send_photo(message.from_user.id, photo, """<b>"Радар биржи"</b> анализирует все минутные свечи акций торгуемых на Московской бирже. Если бот видит повышенный обьем в акции, то он сразу сигнализирует об этом.\n\n<b>Бот уведомляет:</b>\n\n🔸 Какой обьем был куплен.\n🔸 Изменение цены на данном обьеме.\n🔸 Изменение цены за день.\n🔸 О количестве покупателей и продавцов на данном обьеме.\n\n<b>Этот инструмент должен быть у каждого инвестора!</b>""", reply_markup=keyb_for_unsubed, parse_mode=ParseMode.HTML)


@dp.message_handler(lambda message: "📋 Пользовательское соглашение" == message.text)
async def get_user_agreement(message: types.Message):
    await message.reply('Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-07-13-5', disable_web_page_preview=True)

@dp.message_handler(lambda message: message.text.lower() == 'купить подписку' or message.text.lower() == '/subscribe')
async def buy_sub(message: types.Message):
    user_exists = await if_user_exists(message.from_user.id)
    if user_exists:
        if await is_in_payment_system(message.from_user.id):
            if await do_have_paid_sub(message.from_user.id) and not await do_have_free_sub(message.from_user.id):
                await message.answer("Вы уже подписаны", reply_markup=keyb_for_subed)
            elif not await do_have_paid_sub(message.from_user.id) and await do_have_free_sub(message.from_user.id):
                await message.answer("У вас есть бесплатная подписка, при покупке платной подписки она отменится. Если вы готовы продолжить,нажми на кнопку под сообщением", reply_markup=create_not_first_time_buying_kb(message.from_user.id))
            else:
                await message.answer("Купите платную подписку нажав на одну из кнопок", reply_markup=create_not_first_time_buying_kb(message.from_user.id))
        else:
            if await do_have_free_sub(message.from_user.id):
                await message.answer('У вас есть бесплатная подписка. Если купите платную подписку, то она отменится. Если вы готовы так сделать, то нажмите на кнопку под сообщением', reply_markup=create_buying_link(message.from_user.id))
            else:
                await message.answer("Купите платную подписку нажав на одну из кнопок", reply_markup=create_buying_link(message.from_user.id))
    else:
        await add_user(user_id=message.from_user.id)
        await message.answer('Попробуйте еще раз. Вызовите /subscribe или напишите "Купить Подписку"')

@dp.message_handler(lambda message: "Рефералка" == message.text or message.text.lower() == '/ref' )
async def get_your_ref_data(message: types.Message):
    user_exists = await if_user_exists(message.from_user.id)
    if user_exists:
        if await is_in_payment_system(message.from_user.id):
            if await do_have_paid_sub(message.from_user.id) and not await do_have_free_sub(message.from_user.id):
                ref_traffic = await get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await get_money_amount_attracted_by_referer(message.from_user.id)}₽", reply_markup=keyb_for_subed, disable_web_page_preview=True)
            elif not await do_have_paid_sub(message.from_user.id) and await do_have_free_sub(message.from_user.id):
                ref_traffic = await get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await get_money_amount_attracted_by_referer(message.from_user.id)}₽", reply_markup=keyb_for_subed, disable_web_page_preview=True)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
        else:
            if await do_have_free_sub(message.from_user.id):
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await get_money_amount_attracted_by_referer(message.from_user.id)}₽", reply_markup=keyb_for_subed, disable_web_page_preview=True)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        await add_user(user_id=message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)

@dp.message_handler(lambda message: '✅ Подписка' == message.text or message.text.lower() == '/profile')
async def get_profile_data(message: types.Message):
    user_exists = await if_user_exists(message.from_user.id)
    if user_exists:
        if await is_in_payment_system(message.from_user.id):
            if await do_have_paid_sub(message.from_user.id):
                #ref_traffic = db.get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твой ID: {message.from_user.id}\n"+ f"\nУ вас есть еще {await before_end_of_paid_sub(message.from_user.id)} оплаченных дней. \n\nНе пугайтесь если вы отменяли подписку, с вас не снимутся средства, просто у вас еще осталось несколько оплаченных дней после истечения которых вы потеряете доступ к полному функционалу бота!", reply_markup=create_cancel_kb(message.from_user.id))
            elif await do_have_free_sub(message.from_user.id):
                await message.answer(f"Твой ID: {message.from_user.id}\n"+ f"\nУ вас есть еще {await before_end_of_free_sub(message.from_user.id)} дней в бесплатной подписке", reply_markup=create_cancel_kb(message.from_user.id))
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
        else:
            if await do_have_free_sub(message.from_user.id):
                days = await before_end_of_free_sub(message.from_user.id)
                await message.answer(
                    f"Твой ID: {message.from_user.id}\n"+ 
                    f"\nДо конца бесплатной подписки осталось {days} дней", reply_markup=keyb_for_subed
                )
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        await add_user(user_id=message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)


















"""
ADMIN HANDLERS –– ADMIN HANDLERS –– ADMIN HANDLERS –– ADMIN HANDLERS –– ADMIN HANDLERS –– ADMIN HANDLERS 
"""
@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer('Вы отменили все действия, весь прогресс сброшен')

@dp.message_handler(commands=['admin'])
async def admin_things(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer(ADMIN_MESSAGE)
    else:
        await message.answer('Вы не админ')
        
@dp.message_handler(commands=['give_free_sub'])
async def give_free_sub(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer('Вам нужно ввести ID человека которому вы хотите дать бесплатную подписку. ID можно получить вот здесь отправив ссылку на профиль https://t.me/getmy_idbot', disable_web_page_preview=True)
        await state.set_state(GiveFreeSub.choose_id)
    else:
        await message.answer('Вы не админ!')
@dp.message_handler(state=GiveFreeSub.choose_id)
async def give_free_sub_step_choose_user(message: types.Message, state: FSMContext):
    try:
        user_exists = await if_user_exists(int(message.text))
    except:
        await state.finish()
        await message.answer("Что-то пошло не так, начните заново")
    if user_exists:
        if message.text.isdigit():
            if await do_have_free_sub(int(message.text)):
                await state.finish()
                await message.answer("Этот пользователь уже имеет бесплатную подписку")
                return
            elif await do_have_paid_sub(int(message.text)):
                await state.finish()
                await message.answer("Этот пользователь уже имеет подписку оформленную через cloud payments")
            elif not await do_have_paid_sub(int(message.text)) and not await do_have_free_sub(int(message.text)):
                await state.update_data(user_id = message.text)
                await message.answer("Теперь надо ввести число дней на которое будет оформлена бесплатная подписка")
                await state.set_state(GiveFreeSub.choose_period)
        else:
            await state.finish()
            await message.answer("Вы прислали не число. Начните заново вызвав /give_free_sub")
    else:
        await state.reset_state()
        await add_user(user_id=int(message.text))
        await message.answer("Пользователь с таким id не был добавлен в базу данных, но я это исправил. Начните заново вызвав /give_free_sub")
@dp.message_handler(state=GiveFreeSub.choose_period)
async def give_free_sub_step_choose_time(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            user_id = data['user_id']
            try:
                await state.finish()
                await bot.send_message(user_id, f'Вам выдана бесплатная подписка на {message.text} дней')
                await set_free_sub_end(user_id, datetime.now(offset) + timedelta(days=int(message.text)))
                await message.answer(f'Бесплатная подписка на {message.text} дней выдана пользователю и он об этом уведомление')

            except:
                await state.finish()
                await message.answer("Возникла проблема при отправке уведомления пользователю. Он мог заблокировать бота")
    else:
        await state.finish()
        await message.answer("Вы прислали не число. Начните заново вызвав /give_free_sub")

@dp.message_handler(commands=['update_free_sub'])
async def add_days_to_free_sub(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Вам нужно ввести ID человека которому вы хотите дать бесплатную подписку. ID можно получить вот здесь отправив ссылку на профиль https://t.me/getmy_idbot")
        await state.set_state(UpdateFreeSubForOne.choose_id)
    else:
        await message.answer("Вы не админ")

@dp.message_handler(state = UpdateFreeSubForOne.choose_id)
async def set_period_for_free_sub(message: types.Message, state: FSMContext):
    try:
        user_exists = await if_user_exists(int(message.text))
    except:
        await state.finish()
        await message.answer("Что-то пошло не так, начните заново")
    if user_exists:
        if message.text.isdigit():
            if not await do_have_paid_sub(int(message.text)):
                if await do_have_free_sub(int(message.text)):
                    await state.update_data(user_id = message.text)
                    await message.answer('Теперь надо ввести число дней на которое вы хотите продлить бесплатную подписку пользователю')
                    await state.set_state(UpdateFreeSubForOne.choose_period)
                else:
                    await state.finish()
                    await message.answer("У человека нет бесплатной подписки. Прогресс сброшен!")
            else:
                await state.finish()
                await message.answer("Возникла ошибка тк у человека есть платная подписка. Прогресс сброшен!")
        else:
            await state.reset_state()
            await message.answer('Вы должны были ввести число. Прогресс сброшен!')
    else:
        await state.reset_state()
        await add_user(user_id=int(message.text))
        await message.answer('Этого человека нет в бд. \nНачните заново с другим пользователем либо дайте подписку пользователю с которым вы работали сейчас вызвав команду /update_free_sub.')
@dp.message_handler(state = UpdateFreeSubForOne.choose_period)
async def extend_free_sub(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        user_id = None
        async with state.proxy() as data:
            user_id = data['user_id']
        free_sub = await get_free_sub_end(user_id)
        if free_sub is not None:
            free_sub = convert_strdate_to_date(free_sub)
            free_sub = free_sub + timedelta(days=int(message.text))
            try:
                await state.finish()
                await bot.send_message(user_id, f"Вам была продлена бесплатная подписка на {message.text} дней")
                await message.answer("Бесплатная подписка для пользователя продлена")
                await set_free_sub_end(user_id, free_sub)
            except:
                await state.finish()
                await message.answer("Что-то пошло не так на стороне пользователя")
    else: 
        await state.finish()
        await message.answer('Вы прислали не число. Начните заново вызвав команду /extend_free_sub')

@dp.message_handler(commands=['update_paid_sub_for_all'])
async def update_paid_sub_for_all(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        state.set_state(UpdatePaidSubForAll.choose_period)
        await message.answer('Введите число дней на которое вы хотите продлить подписку всем пользователям')
    else:
        await message.answer("Вы не админ")

@dp.message_handler(state=UpdatePaidSubForAll.choose_period)
async def update_sub_choose_days(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await update_sub_for_all(days=int(message.text))
        await state.finish()
        await message.answer("Платная подписка успешно продлена всем пользователям")
    else:
        await state.reset_state()
        await message.answer('Вы ввели не число. Начните заново вызвав команду /update_paid_sub_for_all')

@dp.message_handler(commands=['update_paid_sub_for_one'])
async def update_paid_sub_for_one(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(UpdatePaidSubForOne.choose_id)
        await message.answer('Вам нужно ввести ID человека которому вы хотите продлить платную подписку. ID можно получить вот здесь отправив ссылку на профиль https://t.me/getmy_idbot')
    else:
        await message.answer('Вы не админ')
@dp.message_handler(state=UpdatePaidSubForOne.choose_id)
async def update_paid_sub_for_one_choose_id(message: types.Message, state: FSMContext):
    try:
        user_exists = await if_user_exists(int(message.text))
    except:
        await state.finish()
        await message.answer("Что-то пошло не так, начните заново")
    if user_exists:
        if message.text.isdigit():
            if await is_in_payment_system(int(message.text)):
                if await do_have_paid_sub(int(message.text)) and not await do_have_free_sub(int(message.text)):
                    await state.update_data(user_id = message.text)
                    await message.answer('Теперь надо ввести число дней на которое вы хотите продлить платную подписку пользователю')
                    await state.set_state(UpdatePaidSubForOne.choose_period)
                else: 
                    await state.reset_state()    
                    await message.answer("Этот пользователь не имеет платной подписки.  Начните заново вызвав команду /extend_sub") 
            else:
                await state.reset_state()
                await message.answer("Этот пользователь ни разу не оплачивал подписку.  Начните заново вызвав команду /extend_sub")
        else:
            await state.reset_state()
            await message.answer("Вы сделали неправильный ввод. Начните заново вызвав команду /extend_sub")
    else:
        await state.reset_state()
        await add_user(user_id=int(message.text))
        await message.answer('Этого человека нет в бд. \nНачните заново с другим пользователем вызвав /extend_sub')

@dp.message_handler(state=UpdatePaidSubForOne.choose_period)
async def update_paid_sub_for_one_choose_period(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        user_id = None
        async with state.proxy() as data:
            user_id = data['user_id']
        try:
            await state.finish()
            await update_sub_test(user_id, days=int(message.text))
            await bot.send_message(user_id, f'Вам продлена платная подписка на {message.text} дней')
            await message.answer("Подписка успешно продлена и пользователь об этом уведомлен")
        except Exception as e:
            logging.info(e)
            await state.finish()
            await message.answer('До человека не дошло сообщения тк он заблокировал бота') 
    else:
        await state.reset_state()
        await message.answer('Вы ввели не число, повторите операции вызвав команду /extend_sub')

@dp.message_handler(commands=['check_referal'])
async def check_referal(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(CheckRef.choose_id)
        await message.answer('Вам нужно ввести ID реферала статистику которого вы хотите проверить. ID можно получить вот здесь отправив ссылку на профиль https://t.me/getmy_idbot')
    else:
        await message.answer('Вы не админ')
@dp.message_handler(state=CheckRef.choose_id)
async def get_stat(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        ref_traffic = await get_referer_traffic(int(message.text)) # кол-во людей
        await message.answer(f"Реферальная ссылка пользователя: https://t.me/{BOT_NICK}?start={message.text}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные юзеры: {await get_money_amount_attracted_by_referer(message.from_user.id)}₽")
        await state.reset_state()
    else:
        await state.reset_state()
        await message.answer('Вы неправильно ввели данные. введите только id. Вызовите команду /check_ref снова чтобы повторить процесс')

@dp.message_handler(commands=['make_partner'])
async def make_partner(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(MakePartner.choose_id)
        await message.answer('Вам нужно ввести ID человека которому вы хотите присвоить статус партнера. ID можно получить вот здесь отправив ссылку на профиль https://t.me/getmy_idbot', disable_web_page_preview=True)
    else:
        await message.answer('Вы не админ')

@dp.message_handler(state=MakePartner.choose_id)
async def set_partner_id(message: types.Message, state: FSMContext):
    try:
       await state.finish()
       await set_partner(int(message.text))
       await bot.send_message(message.text, 'Вам просвоен статус партнера')
       await message.answer("Вы присвоили человеку статус партнера и он об этом уведомлен")
    except Exception as e:
       logging.info(e)
       await state.finish()
       await message.answer('До человека не дошло сообщения тк он заблокировал бота. Прогресс сброшен') 
    

@dp.message_handler(commands=['delete_partner'])
async def delete_partner(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(DelPartner.choose_id)
        await message.answer('Вам нужно ввести ID человека у которого вы хотите отнять статус партнера. ID можно получить вот здесь отправив ссылку на профиль https://t.me/getmy_idbot', disable_web_page_preview=True)
    else:
        await message.answer('Вы не админ')
        
@dp.message_handler(state=DelPartner.choose_id)
async def delete_partner_id(message: types.Message, state: FSMContext):
    try:
       await state.finish()
       await del_partner(int(message.text))
       await bot.send_message(message.text, 'Теперь вы не являетесь партнером')
       await message.answer("Вы убрали человеку статус партнера и он об этом уведомлен")
    except Exception as e:
       logging.info(e)
       await state.finish()
       await message.answer('До человека не дошло сообщения тк он заблокировал бота. Прогресс сброшен') 

@dp.message_handler(commands=['push_for_subed'])
async def push_for_subed(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(PushForSubed.input_text)
        await message.answer('Введите текст для рассылки')
    else:
        await message.answer('Вы не админ!')

@dp.message_handler(state=PushForSubed.input_text)
async def send_push(message: types.Message, state: FSMContext):
    subed_users = await get_subed_users()
    for user in subed_users:
        try:
            await bot.send_message(user, message.text)
        except Exception as e:
            pass
    await message.answer('Рассылка отправлена!')
    await state.reset_state()






"""
SENDERS –– SENDERS –– SENDERS –– SENDERS –– SENDERS –– SENDERS –– SENDERS –– SENDERS 
"""
async def send():
    data = await read_json()
    users = await get_subed_users()
    logging.info('send')
    print(data)
    for item in data:
        for user in users:
            try:
                await bot.send_message(
                    int(user),
                    f"#{item['sec_id']} <b>{item['sec_name']}</b>\n\n{item['dir']}Аномальный объем\n"+
                    f"Изменение цены: {item['price_change']}%\n"+
                    f"Объем: {round(float(item['volume_rub'])/1000000, 2)}M₽ ({item['lot_amount']} лотов)\n" + 
                    (f"<b>Покупка: {item['buyers']}%</b> Продажа: {item['sellers']}%\n" if item['buyers'] > item['sellers'] else f"Покупка: {item['buyers']}% <b>Продажа: {item['sellers']}%</b>\n") +
                    f"Время: {item['current_date']} {item['time']}\n"+
                    f"Цена: {item['current_price']}₽\n"+ 
                    f"Изменение за день: {item['day_change']}%\n\n"+
                    "<b>Заметил Радар Биржи</b>\n"
                    f"""<b>Подключить <a href="https://t.me/{BOT_NICK}?start={user}">@{BOT_NICK}</a></b>""",
                    disable_notification=False,
                    parse_mode=types.ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except exceptions.RetryAfter as e:
                time.sleep(e.timeout)
                logging.info(f'блокировка бота на {e.timeout}')
            except Exception as e:
                logging.info(f"{item['sec_name']}\nОшибка отправки\n", e)
                continue
    await clear_json()

async def send_notification_about_subscription():
    data = get_notifications()
    if data:
        for i in data:
            try:
                await bot.send_message(i['receiver'], i['message'])
            except Exception as e:
                logging.info(e)
    write_notifications([])

def schedule_tasks():
    aioschedule.every(60).seconds.do(send)
    aioschedule.every(5).minutes.do(send_notification_about_subscription)


async def main():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    schedule_tasks()
    asyncio.create_task(main())








"""
RUN –– RUN –– RUN –– RUN –– RUN –– RUN –– RUN –– RUN 
"""
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)