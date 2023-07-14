from aiogram import Bot, Dispatcher, executor, types, exceptions

from aiogram.types.message import ContentType
import asyncio
import aioschedule
from db import BotDB
import logging
import time
import moex_async
import datetime as dt
from datetime import datetime, timedelta
from config import API_TOKEN, PAYMENT_TOKEN_TEST, PAYMENT_TOKEN_PROD, BOT_NICK
import pytz
from pytz import timezone
from kb import keyb_for_subed, keyb_for_unsubed


# ___________Configure__logging___________
logging.basicConfig(level=logging.INFO)
offset = dt.timezone(timedelta(hours=3))
volumes_avg_prev = {}
collecting_avg_event = asyncio.Event()
tasks = []



# ___________Initialize__bot__and__dispatcher___________
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
db = BotDB('database.db')


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
    if db.check_if_subed(message.from_user.id) == 0:
        await message.reply("О боте", reply_markup=keyb_for_unsubed)
    else:
        await message.reply("описание бота описание бота описание бота описание бота описание бота описание бота описание бота описание бота", reply_markup=keyb_for_subed)

@dp.message_handler(lambda message: message.text.lower() == "пользовательское соглашение")
async def get_user_agreement(message: types.Message):
    await message.reply('Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-07-13-5',)


#___________Payment__Handlers___________
PRICE = types.LabeledPrice(label='Подписка на 1 месяц', amount=500*100) # 500 rub
@dp.message_handler(lambda message: message.text.lower() == 'купить подписку' or message.text.lower() == '/subscribe')
async def subscribe(message: types.Message):
    # добавить проверку если подписка пользователя активна
    if not db.user_exists(message.from_user.id):
        await message.answer("Вас нет в БД, но я это уже исправил! Вызовите команду /subscribe заново!")
        db.add_user(message.from_user.id)
    else:
        if db.check_if_subed(message.from_user.id) == 1:
            await message.answer("Вы уже подписаны!", reply_markup=keyb_for_subed)
        else:
            if PAYMENT_TOKEN_TEST.split(':')[1] == "TEST":
                await bot.send_message(message.chat.id, 'Тестовый платеж')
            await bot.send_invoice(
                message.chat.id,
                title="Подписка на бота",
                description='Активация подписки на бота на 1 месяц',
                provider_token=PAYMENT_TOKEN_TEST,
                currency='rub',
                photo_url='https://media.istockphoto.com/id/679762242/ru/%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F/%D0%B1%D0%B8%D0%B7%D0%BD%D0%B5%D1%81%D0%BC%D0%B5%D0%BD-%D0%B8%D0%BB%D0%B8-%D1%82%D0%BE%D1%80%D0%B3%D0%BE%D0%B2%D0%B5%D1%86-%D0%BD%D0%B0-%D1%84%D0%BE%D0%BD%D0%B4%D0%BE%D0%B2%D0%BE%D0%BC-%D1%80%D1%8B%D0%BD%D0%BA%D0%B5-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0%D1%8E%D1%89%D0%B8%D0%B9-%D0%B7%D0%B0-%D1%81%D1%82%D0%BE%D0%BB%D0%BE%D0%BC.jpg?s=1024x1024&w=is&k=20&c=OsEncaxRjp-sbXTQUGF7XtFfSHvG03Cvu1JNl8kis7Y=',
                photo_width=416,
                photo_height=234,
                photo_size=416,
                is_flexible=False,
                prices=[PRICE],
                start_parameter='one-month-subscription',
                payload='test-invoice-payload'
            )

@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESFUL PAYMENT")
    payment_info = message.successful_payment.to_python()
    for k, v in  payment_info.items():
        print(f"{k} = {v}")
    # Добавлять пользователя в бд + считать срок окончания подписки
    sub_start = datetime.now(offset)
    sub_end = datetime.now(offset) + timedelta(days=30)
    db.subcribe(message.chat.id, sub_end, sub_start)
    await bot.send_message(message.chat.id, f'Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!', reply_markup=keyb_for_subed)

#___________Referral__Things___________
@dp.message_handler(lambda message: message.text.lower() == 'подписка' or message.text.lower() == '/profile')
async def get_profile_data(message: types.Message):
    if db.user_exists(message.from_user.id):
        if db.check_if_subed(message.from_user.id) == 1:
            ref_traffic = db.get_referer_traffic(message.from_user.id)
            money_paid = db.get_money_amount_attracted_by_referer(message.from_user.id)
            sub_end = datetime.strptime(str(db.get_sub_end(message.from_user.id)), '%Y-%m-%d %H:%M:%S.%f%z')
            sub_end = sub_end.replace(tzinfo=pytz.timezone('Europe/Moscow')) # добавляем информацию о часовом поясе
            before_end_period = sub_end - datetime.now(offset)
            before_end_period = str(before_end_period).replace('days', 'дней')
            dot_index = str(before_end_period).index(',')
            await message.answer(
                f"Твой ID: {message.from_user.id}\n"+ 
                f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + 
                f"Кол-во привлеченных пользователей: {ref_traffic}\n" +
                f"Сколько денег помог привлечь боту: {0 if money_paid == None else money_paid}₽"+
                f"\nДо конца подписки осталось {str(before_end_period)[:dot_index]}", reply_markup=keyb_for_subed
            )
        else:
            await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        db.add_user(message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)



async def process_stock(stock, volume_avg_prev):
    while True:
        await collecting_avg_event.wait() 
        start_time = datetime.now(offset).replace(hour=9, minute=50, second=0, microsecond=0).time()
        end_time = datetime.now(offset).replace(hour=23, minute=50, second=0, microsecond=0).time()
        if end_time >= datetime.now(offset).time() and datetime.now(offset).time() >= start_time:
            try:
                print(1)
                users_arr = db.get_subed_users()
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
                buyers_sellers = moex_async.buyers_vs_sellers1(stock[0])
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
                if check_volume * 20 <= data[4]:
                    for user in users_arr:
                        await bot.send_message(
                            user[0],
                            f"#{data[0]} {data[1]}\n{dir}Аномальный объем\n"+
                            f'Изменение цены: {data[-3]}%\n'+
                            f'Объем: {round(float(data[4])/1000000, 3)}M₽ ({data[-4]} лотов)\n' + 
                            f'Покупка: {data[-2]}% Продажа: {data[-1]}%\n' +
                            f'Время: {current_date[5:]} {current_time}\n'+
                            f'Цена: {data[3]}₽\n'+ 
                            f'Изменение за день: {data[2]}%\n\n'+
                            "<b>Заметил Радар МосБиржи</b>\n"
                            f"""<b>Подключить <a href="https://t.me/{BOT_NICK}?start={user[0]}">@{BOT_NICK}</a></b>""",
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
        await asyncio.sleep(30) 

async def process_stocks():
    await collecting_avg_event.wait() 
    securities = await moex_async.get_securities()
    for stock in securities:
        print(stock[0])
        #task = asyncio.create_task(process_stock(stock, volumes_avg_prev))
        task = process_stock(stock, volumes_avg_prev)
        tasks.append(task)
    for task in tasks:
        asyncio.create_task(task)
        await asyncio.sleep(5)

async def main():
    await process_stocks()

async def unsubscribe():
    data = db.get_user_id_with_end_timestamp()
    current_datetime = datetime.now(offset)
    for row in data:
        user_id = row[0]
        sub_end = row[1]
        sub_end_datetime = datetime.strptime(sub_end, '%Y-%m-%d %H:%M:%S')
        if sub_end_datetime > current_datetime:
            db.unsubcribe(user_id)
            await bot.send_message(user_id, 'У вас кончилась подписка, продлите ее, чтоб пользоваться ботом без ограничений!', reply_markup=keyb_for_unsubed)

async def delivery():
    users = db.get_unsubed_users()
    for user in users:
        user_id = user[0]
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
    aioschedule.every(1).days.at("12:00").do(unsubscribe)
    aioschedule.every(1).days.at("19:00").do(delivery)
    aioschedule.every(1).days.at('01:00').do(collect_volumes_avg)

    #aioschedule.every(1).minutes.do(collect_volumes_avg)
    while True:
        if datetime.now(offset).weekday() < 5: 
            await aioschedule.run_pending()
            await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(collect_volumes_avg())
    asyncio.create_task(main())
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)