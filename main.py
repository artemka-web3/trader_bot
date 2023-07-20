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
    if check_if_subed(message.from_user.id) == 0:
        await message.reply("О боте", reply_markup=keyb_for_unsubed)
    else:
        await message.reply("описание бота описание бота описание бота описание бота описание бота описание бота описание бота описание бота", reply_markup=keyb_for_subed)

@dp.message_handler(lambda message: message.text.lower() == "пользовательское соглашение")
async def get_user_agreement(message: types.Message):
    await message.reply('Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-07-13-5',)

#___________Referral__&&__Subscription__Things___________
@dp.message_handler(lambda message: message.text.lower() == 'купить подписку' or message.text.lower() == '/subscribe')
async def buy_sub(message: types.Message):
    unsubed_users = get_unsubed_users()
    if message.from_user.id in unsubed_users:
        await message.answer('Для того чтобы купить подписку вам нужно определиться, какой тариф вы хотите выбрать. Чтобы купить подписку на нужное время, надмите на кнопку снизу!',  reply_markup=create_buying_link(message.from_user.id))
    else:
        await message.answer('У вас есь подписка')


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'cancel_sub')
async def cancel_subscription(callback_query: types.CallbackQuery):
    cancel_sub(callback_query.from_user.id)
    count_money_attracted_by_one(callback_query.from_user.id)
    await callback_query.answer('Вы успешно отписались ✅')

@dp.message_handler(lambda message: message.text.lower() == 'подписка' or message.text.lower() == '/profile')
async def get_profile_data(message: types.Message):
    if db.user_exists(message.from_user.id):
        if check_if_subed(message.from_user.id):
            ref_traffic = db.get_referer_traffic(message.from_user.id) # кол-во людей
            # money_paid = db.get_money_amount_attracted_by_referer(message.from_user.id) # кол-во денег
            #sub_end = datetime.strptime(str(db.get_sub_end(message.from_user.id)), '%Y-%m-%d %H:%M:%S.%f%z')
            #sub_end = sub_end.replace(tzinfo=pytz.timezone('Europe/Moscow')) # добавляем информацию о часовом поясе
            #before_end_period = sub_end - datetime.now(offset)
            #before_end_period = str(before_end_period).replace('days', 'дней')
            #dot_index = str(before_end_period).index(',')
            await message.answer(
                f"Твой ID: {message.from_user.id}\n"+ 
                f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + 
                f"Кол-во привлеченных пользователей: {ref_traffic}\n" +
                f"Сколько денег помог привлечь боту: {count_money_attracted_by_one(message.from_user.id)}₽"+
                f"\nДо конца подписки осталось {get_sub_end(message.from_user.id)}", reply_markup=c_keyb
            )
        else:
            await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        db.add_user(message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)

#______________ADMIN___PANEL___THINGS__________________
@dp.message_handler(commands=('cancel'), state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    # Сброс состояния пользователя
    await state.reset_state()
    # Или можно использовать await state.finish()
    await message.reply('Вы отменили действие. Весь прогресс сброшен.')

@dp.message_handler(commands=['admin'])
async def admin_things(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Вот команды которые может использовать админ\n"+
            "/free_sub - Отдать кому-то бесплатную подписку при условии что у человека нет активной подписки на сервис\n"+
            "/extend_sub - Продлить подписку всем или кому-то одному при условии что у человека есть активная подписка на сервис\n"+
            "/cancel - сбросить ввод и начать заново\n"+
            "/make_partner - присвоить человеку статус партнера", reply_markup=
        )

@dp.message_handler(commands=['free_sub'])
async def give_free_sub_сhoose_user(message: types.Message, state = FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer('Введите ID пользователя, которому вы хотите дать подписку бесплатно. ID можно получить здесь https://t.me/getmy_idbot')
        await state.set_state(GiveFreeSub.CHOOSE_USER)
    else:
        await message.answer('Вы не админ!')
@dp.message_handler(state=GiveFreeSub.CHOOSE_USER)
async def give_free_sub_step_choose_time(message: types.Message, state: FSMContext):
    is_in = await get_user_id_by_username(message.text)
    is_active = check_if_active(message.text)
    if is_in and not is_active:
        user_id = message.text
        await state.update_data(user_id = user_id)
        await message.answer(f"Отлично, вот id пользователя: {user_id}. Теперь выберите срок на который хотите дать подписку", reply_markup=time_for_sub_keyb)
        await state.set_state(GiveFreeSub.SET_TIME_FOR_SUB)
    else:
        await state.reset_state()
        # Или можно использовать await state.finish()
        await message.reply('ID пользователя не найден либо у него есть активная подписка, начните заново')
@dp.message_handler(state=GiveFreeSub.SET_TIME_FOR_SUB)
async def give_free_sub_step_choose_time(message: types.Message, state: FSMContext):
    user_id = None
    async with state.proxy() as data:
        user_id = data['user_id']
    if message.text == '1 месяц':
        db.set_free_sub_end(user_id, datetime.now(tz=pytz.timezone('Europe/Moscow'))+timedelta(days=30))
        try:
            await bot.send_message(user_id, 'Вам выдана бесплатная подписка на 1 месяц')
            await message.answer('Пользователю выдана подписка на месяц и он об этом уведомлен')
        except Exception as e:
            print(e)
            await state.reset_state()
            await message.answer('При отправке сообщения пользователю что-то пошло не так. Видимо он заблокировал бота!')
    elif message.text == '6 месяцев':
        db.set_free_sub_end(user_id, datetime.now(tz=pytz.timezone('Europe/Moscow'))+timedelta(days=180))
        try:
            await bot.send_message(user_id, 'Вам выдана бесплатная подписка на 6 месяцев')
            await message.answer('Пользователю выдана подписка на пол года и он об этом уведомлен')
        except Exception as e:
            print(e)
            await state.reset_state()
            await message.answer('При отправке сообщения пользователю что-то пошло не так. Видимо он заблокировал бота!')
    elif message.text == 'Год':
        db.set_free_sub_end(user_id, datetime.now(tz=pytz.timezone('Europe/Moscow'))+timedelta(days=365))
        try:
            await bot.send_message(user_id, 'Вам выдана бесплатная подписка на 1 год')
            await message.answer('Пользователю выдана подписка на год и он об этом уведомлен')
        except Exception as e:
            print(e)
            await state.reset_state()
            await message.answer('При отправке сообщения пользователю что-то пошло не так. Видимо он заблокировал бота!')
    await state.finish()      

@dp.message_handler(commands=['extend_sub'])
async def extend_sub(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Вы хотите продлить подписку всем или только одного", reply_markup=one_or_m)
        await state.set_state(ExtendSub.CHOSE_MODE)
    else:
        await message.answer('Вы не админ!')
@dp.message_handler(state=ExtendSub.CHOSE_MODE)
async def extend_sub(message: types.Message, state: FSMContext):
    if message.text == "Один":
        await message.answer('Введите ID пользователя, которому вы хотите продлить подписку. ID можно получить здесь https://t.me/getmy_idbot')
        await state.set_state(ExtendSub.CHOOSE_ID)
    elif message.text == 'Несколько':
        await message.answer("Скажите на сколько дней вы хотите продлить подписку пользователям. В")
        await state.set_state(ExtendSub.SET_DAYS)
    else:
        await message.answer("Попробуйте заново. Вызовите эту команду заново чтобы повторить процесс")
        await state.finish()

@dp.message_handler(state=ExtendSub.SET_DAYS)
async def extend_sub_for_all(message: types.Message, state: FSMContext):
    try:
        update_sub_for_all(int(message.text))
        await message.answer(f"Подписка успешно продлена всем юзерам на {message.text} дней")
        await state.finish()
    except Exception as e:
        print(str(e))

@dp.message_handler(state=ExtendSub.CHOOSE_ID)
async def extend_sub_id(message: types.Message, state: FSMContext):
    is_in = await get_user_id_by_username(message.text)
    is_subed = check_if_active(message.text)
    if is_in and is_subed:
        user_id = message.text
        await state.update_data(user_id = user_id)
        await message.answer(f"Отлично, вот id пользователя: {user_id}. Теперь выберите срок на который хотите дать подписку", reply_markup=time_for_sub_keyb)
        await state.set_state(ExtendSub.SET_EXTEND_TIME)
    else:
        await state.reset_state()
        # Или можно использовать await state.finish()
        await message.reply('ID пользователя не найден либо у него неактивная подписка, начните заново с другим пользователем')
@dp.message_handler(state=ExtendSub.SET_EXTEND_TIME)
async def extend_sub_date(message: types.Message, state: FSMContext):
    user_id = None
    async with state.proxy() as data:
        user_id = data['user_id']
    if message.text == '1 месяц':
        update_sub(user_id, days=30)
        try:
            await bot.send_message(user_id, 'Вам продлена подписка на 1 месяц')
            await message.answer('Пользователю продлена подписка на месяц и он об этом уведомлен')
        except Exception as e:
            print(e)
            await state.reset_state()
            await message.answer('При отправке сообщения пользователю что-то пошло не так. Видимо он заблокировал бота!')
    elif message.text == '6 месяцев':
        update_sub(user_id, days=180)
        try:
            await bot.send_message(user_id, 'Вам продлена подписка на 6 месяцев')
            await message.answer('Пользователю продлена подписка на пол года и он об этом уведомлен')
        except Exception as e:
            print(e)
            await state.reset_state()
            await message.answer('При отправке сообщения пользователю что-то пошло не так. Видимо он заблокировал бота!')
    elif message.text == 'Год':
        update_sub(user_id, days=365)
        try:
            await bot.send_message(user_id, 'Вам выдана бесплатная подписка на 1 год')
            await message.answer('Пользователю продлена подписка на год и он об этом уведомлен')
        except Exception as e:
            print(e)
            await state.reset_state()
            await message.answer('При отправке сообщения пользователю что-то пошло не так. Видимо он заблокировал бота!')
    await state.finish()    

@dp.message_handler(commands=['make_partner'])
async def make_partner(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer('Введите ID пользователя, которому вы хотите присвоить статус партнера. ID можно получить здесь https://t.me/getmy_idbot')
        await state.set_state(MakePartner.CHOOSE_ID)
    else:
        await message.answer('Вы не админ!')
@dp.message_handler(state=MakePartner.CHOOSE_ID)
async def make_partner_id(message: types.Message, state: FSMContext):
    is_in = await get_user_id_by_username(message.text)
    if is_in:
        user_id = message.text
        if db.is_partner(user_id):
            await message.answer('Этот человек уже партнер')
            await state.reset_state()
        db.set_partner(user_id)
        await message.answer(f"Отлично, теперь этот человек является партнером")
        await state.reset_state()
    else:
        await state.finish()
        await message.reply('ID пользователя не найден, начните заново')


#_____АСИНХРОННЫЕ__ФУНКЦИИ__ДЛЯ__ВЫПОЛНЕНИЯ__ОСНОВНОГО__ФУНКЦИОНАЛА
async def process_stock(stock, volume_avg_prev):
    while True:
        await collecting_avg_event.wait() 
        start_time = datetime.now(offset).replace(hour=9, minute=50, second=0, microsecond=0).time()
        end_time = datetime.now(offset).replace(hour=23, minute=50, second=0, microsecond=0).time()
        if end_time >= datetime.now(offset).time() and datetime.now(offset).time() >= start_time:
            try:
                print(1)
                users_arr = get_subed_users()
                current_date = (datetime.now(offset)).strftime('%Y-%m-%d')
                current_hour = ("0" +str(datetime.now(offset).hour) if len(str(datetime.now(offset).hour)) < 2 else str(datetime.now(offset).hour))
                current_minute = ("0" +str(datetime.now(offset).minute) if len(str(datetime.now(offset).minute)) < 2 else str(datetime.now(offset).minute))
                current_time = str(current_hour) +":"+ str(current_minute)
                stock_data = await moex_async.get_stock_data(stock[0])  
                print(stock_data)
                sec_id = stock_data[0] # #
                sec_name = stock_data[1] 
                lot_size = stock_data[2]
                day_change = stock_data[3] # %
                current_stock_data = await moex_async.get_current_stock_volume(stock[0])
                current_price = current_stock_data[1] # рублей
                volume_rub = current_stock_data[4] # М рублей
                volume_shares = current_stock_data[5] 
                lot_amount = round(volume_shares / lot_size, 3) # лотов
                price_change = await moex_async.get_price_change(stock[0]) # %
                buyers_sellers = await moex_async.buyers_vs_sellers1(stock[0])
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
                if check_volume * 50 <= data[4]:
                    for user in users_arr:
                        await bot.send_message(
                            int(user),
                            f"#{data[0]} {data[1]}\n{dir}Аномальный объем\n"+
                            f'Изменение цены: {data[-3]}%\n'+
                            f'Объем: {round(float(data[4])/1000000, 3)}M₽ ({data[-4]} лотов)\n' + 
                            f'Покупка: {data[-2]}% Продажа: {data[-1]}%\n' +
                            f'Время: {current_date[5:]} {current_time}\n'+
                            f'Цена: {data[3]}₽\n'+ 
                            f'Изменение за день: {data[2]}%\n\n'+
                            "<b>Заметил Радар МосБиржи</b>\n"
                            f"""<b>Подключить <a href="https://t.me/{BOT_NICK}?start={user}">@{BOT_NICK}</a></b>""",
                            disable_notification=False,
                            parse_mode=types.ParseMode.HTML,
                            reply_markup=keyb_for_subed
                        )
            except exceptions.RetryAfter as e:
                asyncio.sleep(e.timeout)
            except Exception as e:
                print(e)
        else:
            print(f'Торги не идут {stock[0]}')
        await asyncio.sleep(60) 

async def process_stocks():
    await collecting_avg_event.wait() 
    securities = await moex_async.get_securities()
    for stock in securities:
        # check if stock[0] in csv
        async with aiofiles.open('shares.csv', mode='r') as reader:
            async for row in aiocsv.AsyncDictReader(reader, delimiter='\n'):
                if row is not None:
                    if row['Полное название акций ,тикет,сокращённое название '] is not None:
                        if row['Полное название акций ,тикет,сокращённое название '].split(',')[1] == stock[0]:
                            print(stock[0])
                            task = process_stock(stock, volumes_avg_prev)
                            tasks.append(task)
        #task = asyncio.create_task(process_stock(stock, volumes_avg_prev))
    for task in tasks:
        asyncio.create_task(task)
        await asyncio.sleep(5)

async def main():
    await process_stocks()

async def get_user_id_by_username(user_id):
    try:
        all_users = db.get_all_users()
        for user in all_users:
            if str(user) == str(user_id):
                return True
        return False
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return False

async def delivery():
    users = get_unsubed_users()
    for user_id in users:
        await bot.send_message(user_id, 'У тебя нет подписки на нашего бота, советуем тебе оформить ее как можно скорее и приглашать своих друзей сюда. Вызови /subscribe', reply_markup=keyb_for_unsubed)

async def collect_volumes_avg():
    global volumes_avg_prev
    collecting_avg_event.clear() 

    volumes_avg_prev = await moex_async.get_prev_avg_volume(volumes_avg_prev)
    collecting_avg_event.set() 
    return volumes_avg_prev

async def schedule_collecting_volumes():
    await collect_volumes_avg()

async def scheduler():
    # aioschedule.every(1).days.at("12:00").do(unsubscribe)
    aioschedule.every(1).days.at("19:00").do(delivery)
    aioschedule.every(1).days.at('01:00').do(collect_volumes_avg)

    #aioschedule.every(1).minutes.do(collect_volumes_avg)
    while True:
        if datetime.now(offset).weekday() < 5: 
            await aioschedule.run_pending()
            await asyncio.sleep(1)


async def on_startup(_):
    #asyncio.create_task(collect_volumes_avg())
    asyncio.create_task(main())
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)