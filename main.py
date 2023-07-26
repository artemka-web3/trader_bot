from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
import asyncio
import aioschedule
from db import BotDB
import logging
import time
import moex_async
import datetime as dt
from datetime import datetime, timedelta
from config import *
import pytz
from pytz import timezone
from kb import *
import aiofiles
import aiocsv
from cp import *
from fsm import *


# ___________Configure__logging___________
logging.basicConfig(level=logging.INFO)
offset = dt.timezone(timedelta(hours=3))
volumes_avg_prev = {}
collecting_avg_event = asyncio.Event()
tasks = []



# ___________Initialize__bot__and__dispatcher___________
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = BotDB('prod.db')

@dp.message_handler(lambda message: message.text.lower() == 'о боте. руководство' or message.text.lower() == '/start' or message.text.lower() == '/help')
async def send_welcome(message: types.Message):
    if not db.user_exists(message.from_user.id):
        start_command = message.text
        referer_id = str(start_command[7:])
        if str(referer_id) != '':
            if str(referer_id) != str(message.from_user.id):
                db.add_user(message.from_user.id, int(referer_id))
                try:
                    await bot.send_message(int(referer_id), 'По вашей ссылке зарегался новый юзер', reply_markup=keyb_for_unsubed)
                except:
                    pass
            else:
                db.add_user(message.from_user.id)
                await message.answer("Нельзя регаться по своей же реф. ссылке!", reply_markup=keyb_for_unsubed)
        else:
            db.add_user(message.from_user.id)
    if is_in_pay_sys(message.from_user.id) and check_if_subed(message.from_user.id):
        await message.reply("О боте", reply_markup=keyb_for_subed)
    else:
        await message.reply("описание бота описание бота описание бота описание бота описание бота описание бота описание бота описание бота", reply_markup=keyb_for_unsubed)

@dp.message_handler(lambda message: message.text.lower() == "пользовательское соглашение")
async def get_user_agreement(message: types.Message):
    await message.reply('Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-07-13-5')

#___________Referral__&&__Subscription__Things___________
@dp.message_handler(lambda message: message.text.lower() == 'купить подписку' or message.text.lower() == '/subscribe')
async def buy_sub_first(message: types.Message):
    if is_in_pay_sys(message.from_user.id):
        if check_if_subed(message.from_user.id) and not do_have_free_sub(message.from_user.id):
            await message.answer("Вы уже подписаны", reply_markup=keyb_for_subed)
        elif not check_if_subed(message.from_user.id) and do_have_free_sub(message.from_user.id):
            await message.answer("У вас есть бесплатная подписка, при покупке платной подписки она отменится. Если вы готовы продолжить,нажми на кнопку под сообщением", reply_markup=ex_b_keyb)
    else:
        if do_have_free_sub(message.from_user.id):
            await message.answer('У вас есть бесплатная подписка. Если купите платную подписку, то она отменится. Если вы готовы так сделать, то нажмите на кнопку под сообщением', reply_markup=create_buying_link(message.from_user.id))
        else:
            await message.answer("Купите платную подписку нажав на одну из кнопок", reply_markup=create_buying_link(message.from_user.id))


@dp.callback_query_handler()
async def buy_sub_second_more(callback_query: types.CallbackQuery):
    if callback_query.data == 'exb_month':
        buy_not_first_time(callback_query.from_user.id, 30)
        db.set_free_sub_end(callback_query.from_user.id, None)
        await callback_query.answer("Подписка успешно продлена на 30 дней ✅")
    elif callback_query.data == 'exb_semi_year':
        buy_not_first_time(callback_query.from_user.id, 180)
        db.set_free_sub_end(callback_query.from_user.id, None)
        await callback_query.answer("Подписка успешно продлена на пол года ✅")
    elif callback_query.data == 'exb_year':
        buy_not_first_time(callback_query.from_user.id, 365)
        db.set_free_sub_end(callback_query.from_user.id, None)
        await callback_query.answer("Подписка успешно продлена на год ✅")


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'cancel_sub')
async def cancel_subscription(callback_query: types.CallbackQuery):
    cancel_sub(callback_query.from_user.id)
    count_money_attracted_by_one(callback_query.from_user.id)
    await callback_query.answer('Вы успешно отписались ✅')

@dp.message_handler(commands=['ref'])
async def get_yo_ref_data(message: types.Message):
    if db.user_exists(message.from_user.id):
        if is_in_pay_sys(message.from_user.id):
            if check_if_subed(message.from_user.id) and not do_have_free_sub(message.from_user.id):
                ref_traffic = db.get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\n", reply_markup=keyb_for_subed)
            elif not check_if_subed(message.from_user.id) and do_have_free_sub(message.from_user.id):
                ref_traffic = db.get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\n", reply_markup=keyb_for_subed)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
        else:
            if do_have_free_sub(message.from_user.id):
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\n", reply_markup=keyb_for_subed)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        db.add_user(message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)

@dp.message_handler(lambda message: message.text.lower() == 'подписка' or message.text.lower() == '/profile')
async def get_profile_data(message: types.Message):
    if db.user_exists(message.from_user.id):
        if is_in_pay_sys(message.from_user.id):
            if check_if_subed(message.from_user.id):
                #ref_traffic = db.get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(
                    f"Твой ID: {message.from_user.id}\n"+ 
                    f"\nДо конца подписки осталось {get_sub_end(message.from_user.id)} дней", reply_markup=c_keyb
                )
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
        else:
            if do_have_free_sub(message.from_user.id):
                await message.answer(
                    f"Твой ID: {message.from_user.id}\n"+ 
                    f"\nДо конца бесплатной подписки осталось {before_end_of_free_sub(message.from_user.id)} дней", reply_markup=keyb_for_subed
                )
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        db.add_user(message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)

#______________ADMIN___PANEL___THINGS__________________
@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    # Сброс состояния пользователя
    await state.reset_state()
    # Или можно использовать await state.finish()
    await message.reply('Вы отменили действие. Весь прогресс сброшен.', reply_markup=keyb_for_subed)

@dp.message_handler(commands=['admin'])
async def admin_things(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("Вот команды которые может использовать админ:\n"+
            "/free_sub - Отдать кому-то бесплатную подписку при условии что у человека нет активной подписки на сервис\n"+
            "/extend_sub_for_paid_users - Продлить подписку всем или кому-то одному при условии что у человека есть активная платная подписка на сервис\n"+
            "/make_partner - присвоить человеку статус партнера\n"+
            "/extend_free_sub - продление бесплатной подписки \n"+
            "/cancel - сбросить ввод и начать заново\n"
        )

@dp.message_handler(commands=['free_sub'])
async def give_free_sub(message: types.Message, state = FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer('Вам нужно ввести ID человека которому вы хотите дать бесплатную подписку. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot')
        await state.set_state(GiveFreeSub.CHOOSE_USER)
    else:
        await message.answer('Вы не админ!')
@dp.message_handler(state=GiveFreeSub.CHOOSE_USER)
async def give_free_sub_step_choose_user(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if check_if_subed(int(message.text)) and is_in_pay_sys(int(message.text)):
            await state.finish()
            await message.answer("Этот пользователь имеет подписку оформленную через cloud payments")
        elif not check_if_subed(int(message.text)) and is_in_pay_sys(int(message.text)):
            await state.update_data(user_id = message.text)
            await message.answer("Теперь надо ввести число дней на которое будет оформлена бесплатная подписка")
            await state.set_state(GiveFreeSub.SET_TIME_FOR_SUB)
        else:
            await state.update_data(user_id = message.text)
            await message.answer("Теперь надо ввести число дней на которое будет оформлена бесплатная подписка")
            await state.set_state(GiveFreeSub.SET_TIME_FOR_SUB)

    else:
        await message.answer("Вы прислали не число. Начните заново вызвав /free_sub")
        await state.finish()

@dp.message_handler(state=GiveFreeSub.SET_TIME_FOR_SUB)
async def give_free_sub_step_choose_time(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            user_id = data['user_id']
            try:
                await bot.send_message(user_id, f'Вам выдана бесплатная подписка на {message.text} дней')
                db.set_free_sub_end(user_id, datetime.now() + timedelta(days=int(message.text)))
                await message.answer(f'Бесплатная подписка на {message.text} дней выдана пользователю и он об этом уведомление')

            except:
                await state.finish()
                await message.answer("Возникла проблема при отправке уведомления пользователю. Он мог заблокировать бота")
            await state.finish()
    else:
        await message.answer("Вы прислали не число. Начните заново вызвав /free_sub")
        await state.finish()

@dp.message_handler(commands=['extend_free_sub'])
async def extend_free_sub(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Вы хотите продлить бесплатную подписку одному или всем у кого есть бесплатная подписка.", reply_markup=one_or_m)
        await state.set_state(ExtendFreeSub.CHOSE_MODE)
    else:
        await message.answer("Вы не админ")
@dp.message_handler(state= ExtendFreeSub.CHOSE_MODE)
async def extend_free_sub_mode(message: types.Message, state: FSMContext):
    if message.text == 'Один':
        await message.answer('Введите ID пользователя которому хотите продлить бесплатную подписку. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot')
        await state.set_state(ExtendFreeSub.CHOOSE_ID)
    elif message.text == 'Несколько':
        await message.answer("На какое кол-во дней вы хотите продлить бесплатную подписку польователям?")
        await state.set_state(ExtendFreeSub.SET_TIME_FOR_ALL)
    else:
        await state.reset_state()
        await message.answer('Вы должны были нажать на кнопку')

@dp.message_handler(state= ExtendFreeSub.SET_TIME_FOR_ALL)
async def extend_free_sub_all(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        users_with_free = get_users_with_free_sub()
        for user_id in users_with_free:
            free_sub = db.get_free_sub_end(int(user_id))
            if free_sub is not None:
                free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
                free_sub = free_sub + timedelta(days=int(message.text))
                db.set_free_sub_end(int(user_id), free_sub)
    else:
        await state.reset_state()
        await message.answer('Вы должны были ввести число')

@dp.message_handler(state= ExtendFreeSub.CHOOSE_ID)
async def extend_free_sub_id(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if is_in_pay_sys(message.text) and not check_if_subed(int(message.text)):
            if do_have_free_sub(int(message.text)):
                await state.update_data(user_id = message.text)
                await message.answer('Теперь надо ввести число дней на которое вы хотите продлить бесплатную подписку пользователю')
                await state.set_state(ExtendFreeSub.SET_TIME)
            else:
                await state.finish()
                await message.answer("У человека нет бесплатной подписки")
        elif not is_in_pay_sys(int(message.text)) and do_have_free_sub(int(message.text)):
            await state.update_data(user_id = message.text)
            await message.answer('Теперь надо ввести число дней на которое вы хотите продлить бесплатную подписку пользователю')
            await state.set_state(ExtendFreeSub.SET_TIME)
        else:
            await state.finish()
            await message.answer("Возникла ошибка тк у человека есть платная подписка")
    else:
        await state.reset_state()
        await message.answer('Вы должны были ввести число')

@dp.message_handler(state= ExtendFreeSub.SET_TIME)
async def extend_free_sub_choose_date_for_one(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        user_id = None
        async with state.proxy() as data:
            user_id = data['user_id']
        free_sub = db.get_free_sub_end(user_id)
        if free_sub is not None:
            free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
            free_sub = free_sub + timedelta(days=int(message.text))
            try:
                await bot.send_message(user_id, "Вам была продлена бесплатная подписка")
                await message.answer("Бесплатная подписка для пользователя продлена")
                db.set_free_sub_end(user_id, free_sub)
            except:
                await message.answer("Что-то пошло не так на стороне пользователя")
                await state.finish()
        await state.finish()
    else: 
        await state.finish()
        await message.answer('Вы прислали не число. Начните заново вызвав команду /extend_free_sub')



@dp.message_handler(commands=['extend_sub_for_paid_users'])
async def extend_sub(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Вы хотите продлить платную подписку кому-то конкретному или всем юзерам?", reply_markup=one_or_m)
        await state.set_state(ExtendSub.CHOSE_MODE)
    else:
        await message.answer('Вы не админ!')

        
@dp.message_handler(state=ExtendSub.CHOSE_MODE)
async def extend_sub_one_or_m(message: types.Message, state: FSMContext):
    if message.text == "Один":
        await message.answer('Вам нужно ввести ID человека которому вы хотите продлить платную подписку. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot')
        await state.set_state(ExtendSub.CHOOSE_ID)
    elif message.text == 'Несколько':
        await message.answer('На какое кол-во дней вы хотите продлить платную подписку пользователям? Ответьте числом')
        await state.set_state(ExtendSub.SET_DAYS_M)
    else:
        await state.reset_state()
        await message.answer('Вы должны были нажать на кнопку')


@dp.message_handler(state=ExtendSub.SET_DAYS_M)
async def extend_sub_for_all(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        update_sub_for_all(days=int(message.text))
        await state.finish()
        await message.answer("Платная подписка успешно продлена всем пользователям")
    else:
        await state.reset_state()
        await message.answer('Вы ввели не число. Начните заново вызвав команду /extend_sub')

@dp.message_handler(state=ExtendSub.CHOOSE_ID)
async def extend_sub_id(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if is_in_pay_sys(int(message.text)):
            if check_if_subed(int(message.text)):
                if do_have_free_sub(int(message.text)) == False:
                    await state.update_data(user_id = message.text)
                    await message.answer('Теперь надо ввести число дней на которое вы хотите продлить платную подписку пользователю')
                    await state.set_state(ExtendSub.SET_EXTEND_TIME_O)
                else:
                    await message.answer("У этого пользователя есть бесплатная подписка, вы не можете продлить ему платную без его предварительного согласия, он должен купить ее сам. \n  Начните заново вызвав команду /extend_sub")
                    await state.reset_state()
            else: 
                await message.answer("Этот пользователь не имеет платной подписки.  Начните заново вызвав команду /extend_sub") 
                await state.reset_state()    
        else:
            await message.answer("Этот пользователь ни разу не оплачивал подписку.  Начните заново вызвав команду /extend_sub")
            await state.reset_state()
    else:
        await state.reset_state()
        await message.answer("Вы сделали неправильный ввод. Начните заново вызвав команду /extend_sub")

@dp.message_handler(state=ExtendSub.SET_EXTEND_TIME_O)
async def extend_sub_date(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        user_id = None
        async with state.proxy() as data:
            user_id = data['user_id']
        try:
            await bot.send_message(user_id, f'Вам продлена платная подписка на {message.text} дней')
            update_sub(user_id, days=int(message.text))
            await message.answer("Подписка успешно продлена и пользователь об этом уведомлен")
        except:
            await message.answer('До человека не дошло сообщения тк он заблокировал бота') 
        await state.finish()
    else:
        await state.reset_state()
        await message.answer('Вы ввели не число, повторите операции вызвав команду /extend_sub')

@dp.message_handler(commands=['make_partner'])
async def make_partner(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(MakePartner.CHOOSE_ID)
        await message.answer('Вам нужно ввести ID человека которому вы хотите присвоить статус партнера. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot')
    else:
        await message.answer("Вы не админ")

@dp.message_handler(state=MakePartner.CHOOSE_ID)
async def make_partner_id(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if db.is_partner(int(message.text)):
            await message.answer("Этот человек уже партнер")
            await state.finish()
            return
        if check_if_subed(int(message.text)) or do_have_free_sub(int(message.text)):
            await state.finish()
            try:
                await bot.send_message(message.text, 'Вам просвоен статус партнера')
                await message.answer("Вы присвоили человеку статус партнера и он об этом уведомлен")
                db.set_partner(int(message.text))
            except:
                await message.answer('До человека не дошло сообщения тк он заблокировал бота') 
            await state.finish()
        else:
            await message.answer("Человек которому вы хотите присвоить статус партнерта не подписан на бота!")
            await state.reset_state()
    else:
        await state.reset_state()
        await message.answer('Повторите все заново вызвав команду /make_partner. Вы ввели не число!') 



#_____АСИНХРОННЫЕ__ФУНКЦИИ__ДЛЯ__ВЫПОЛНЕНИЯ__ОСНОВНОГО__ФУНКЦИОНАЛА
async def process_stock(stock, volume_avg_prev, coef):
    while True:
        await collecting_avg_event.wait() 
        start_time = datetime.now(offset).replace(hour=9, minute=50, second=0, microsecond=0).time()
        end_time = datetime.now(offset).replace(hour=23, minute=50, second=0, microsecond=0).time()
        if end_time >= datetime.now(offset).time() and datetime.now(offset).time() >= start_time and datetime.now(offset).weekday() < 5:
            try:
                current_date = (datetime.now(offset)).strftime('%Y-%m-%d')
                current_hour = ("0" +str(datetime.now(offset).hour) if len(str(datetime.now(offset).hour)) < 2 else str(datetime.now(offset).hour))
                current_minute = ("0" +str(datetime.now(offset).minute) if len(str(datetime.now(offset).minute)) < 2 else str(datetime.now(offset).minute))
                current_second = ("0" +str(datetime.now(offset).second) if len(str(datetime.now(offset).second)) < 2 else str(datetime.now(offset).second))
                if current_second == 55:
                    users_arr = db.get_all_users()
                    current_time = str(current_hour) +":"+ str(current_minute)
                    stock_data = await moex_async.get_stock_data(stock[0]) 
                    print(stock_data)
                    sec_id = stock_data[0] # #
                    sec_name = stock_data[1] 
                    lot_size = stock_data[2]
                    day_change = stock_data[3] # %
                    current_stock_data = await moex_async.get_current_stock_volume(stock[0], current_time)
                    current_price = current_stock_data[1] # рублей
                    volume_rub = current_stock_data[4] # М рублей
                    volume_shares = current_stock_data[5] 
                    lot_amount = round(volume_shares / lot_size, 2) # лотов
                    price_change = await moex_async.get_price_change(stock[0], current_time) # %
                    price_change_status = 0  #  ноль измнений
                    if price_change > 0:
                        price_change_status = 1
                    elif price_change < 0:
                        price_change_status = 2

                    buyers_sellers = await moex_async.buyers_vs_sellers1(price_change_status)
                    buyers = buyers_sellers[0] # %
                    sellers = buyers_sellers[1] # %
                    data = [sec_id, sec_name, day_change, current_price, volume_rub, lot_amount, price_change, buyers, sellers]
                    dir = '🔵'
                    if data[-3] > 0:
                        dir = "🟢"
                    elif data[-3] < 0:
                        dir = "🔴"
                    print(volume_avg_prev[stock[0]])
                    check_volume = volume_avg_prev[stock[0]]
                    print("CHECK VOLUME: ", check_volume)
                    print("DATA 4: ", data[4])
                    if check_volume * coef <= data[4] and data[4] > 1000000:
                        if users_arr:
                            for user in users_arr:
                                if user[0] in get_subed_users() or do_have_free_sub(user[0]):
                                    await bot.send_message(
                                        int(user[0]),
                                        f"#{data[0]} {data[1]}\n{dir}Аномальный объем\n"+
                                        f'Изменение цены: {data[-3]}%\n'+
                                        f'Объем: {round(float(data[4])/1000000, 2)}M₽ ({data[-4]} лотов)\n' + 
                                        (f'<b>Покупка: {data[-2]}%</b> Продажа: {data[-1]}%\n' if data[-2] > data[-1] else f'Покупка: {data[-2]}% <b>Продажа: {data[-1]}%</b>\n') +
                                        f'Время: {current_date[5:]} {current_time}\n'+
                                        f'Цена: {data[3]}₽\n'+ 
                                        f'Изменение за день: {data[2]}%\n\n'+
                                        "<b>Заметил Радар МосБиржи</b>\n"
                                        f"""<b>Подключить <a href="https://t.me/{BOT_NICK}?start={user}">@{BOT_NICK}</a></b>""",
                                        disable_notification=False,
                                        parse_mode=types.ParseMode.HTML
                                    )
            except exceptions.RetryAfter as e:
                time.sleep(e.timeout)
            except Exception as e:
                print(e)
        else:
            print(f'Торги не идут {stock[0]}')
        # await asyncio.sleep(60) 

async def process_stocks():
    await collecting_avg_event.wait() 
    securities = await moex_async.get_securities()
    for stock in securities:
        # check if stock[0] in csv
        async with aiofiles.open('shares_v2.csv', mode='r') as reader:
            async for row in aiocsv.AsyncDictReader(reader, delimiter='\n'):
                if row is not None:
                    if row['Полное название акций ,тикет,сокращённое название ,ликвидность'] is not None:
                        if row['Полное название акций ,тикет,сокращённое название ,ликвидность'].split(',')[1] == stock[0]:
                            liq_id = row['Полное название акций ,тикет,сокращённое название ,ликвидность'].split(',')[-1]
                            coef = 50
                            if liq_id == 0:
                                coef = 200
                            task = process_stock(stock, volumes_avg_prev, coef)
                            tasks.append(task)
        #task = asyncio.create_task(process_stock(stock, volumes_avg_prev))
    for task in tasks:
        asyncio.create_task(task)
        await asyncio.sleep(5) 

async def main():
    await process_stocks()

async def delivery():
    users = get_unsubed_users()
    if users:
        for user_id in users:
            await bot.send_message(user_id, 'У тебя нет подписки на нашего бота, советуем тебе оформить ее как можно скорее и приглашать своих друзей сюда. Вызови /subscribe')

async def collect_volumes_avg():
    global volumes_avg_prev
    collecting_avg_event.clear() 
    if datetime.now(offset).weekday() < 5:
        volumes_avg_prev = await moex_async.get_prev_avg_months(volumes_avg_prev, 1)
        collecting_avg_event.set() 
        return volumes_avg_prev
    else:
        collecting_avg_event.set() 
        return {}

async def schedule_collecting_volumes():
    await collect_volumes_avg()

async def scheduler():
    # aioschedule.every(1).days.at("12:00").do(unsubscribe)
    aioschedule.every(1).days.at("19:00").do(delivery)
    aioschedule.every(1).days.at('01:00').do(collect_volumes_avg)
    #aioschedule.every(1).minutes.do(collect_volumes_avg)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(collect_volumes_avg())
    asyncio.create_task(main())
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)