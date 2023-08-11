from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
from datetime import datetime, timedelta
from aiodb import BotDB
from config import *
from pytz import timezone
from kb import *
from fsm import *
from cp import *
from moex_async import *
from db_import import db

import asyncio
import aioschedule
import logging
import time
import datetime as dt
import pytz
import aiofiles
import aiocsv


# ___________Configure__logging___________
logging.basicConfig(level=logging.INFO)
offset = dt.timezone(timedelta(hours=3))
volumes_avg_prev = {}
collecting_avg_event = asyncio.Event()
another_share_event = asyncio.Event()

tasks = []



# ___________Initialize__bot__and__dispatcher___________
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(lambda message: 'ℹ️ О боте. Руководство' == message.text or message.text.lower() == '/start' or message.text.lower() == '/help')
async def send_welcome(message: types.Message):
    user_exists = await db.user_exists(message.from_user.id)
    if not user_exists:
        start_command = message.text
        referer_id = str(start_command[7:])
        if str(referer_id) != '':
            if str(referer_id) != str(message.from_user.id):
                await db.add_user(message.from_user.id, int(referer_id))
                try:
                    await bot.send_message(int(referer_id), 'По вашей ссылке зарегался новый юзер', reply_markup=keyb_for_unsubed)
                except:
                    pass
            else:
                await db.add_user(message.from_user.id)
                await message.answer("Нельзя регаться по своей же реф. ссылке!", reply_markup=keyb_for_unsubed)
        else:
            await db.add_user(message.from_user.id)

    if await is_in_pay_sys(message.from_user.id) and await check_if_subed(message.from_user.id):
        await message.reply(""""Радар биржи" анализирует все минутные свечи акций торгуемых на московской бирже.\nЕсли бот видит повышенные обьемы в акции, то он сразу сигнализирует об этом.\n\nБот уведомляет:\n🔸 Какой обьем был куплен\n🔸 Изменение цены на данном обьеме\n🔸 Изменение цены за день в акции.\n🔸 О количестве покупателей и продавцов на данном обьеме.""", reply_markup=keyb_for_subed)
    else:
        await message.reply(""""Радар биржи" анализирует все минутные свечи акций торгуемых на московской бирже.\nЕсли бот видит повышенные обьемы в акции, то он сразу сигнализирует об этом.\n\nБот уведомляет:\n🔸 Какой обьем был куплен\n🔸 Изменение цены на данном обьеме\n🔸 Изменение цены за день в акции.\n🔸 О количестве покупателей и продавцов на данном обьеме.""", reply_markup=keyb_for_unsubed)

@dp.message_handler(lambda message: "📋 Пользовательское соглашение" == message.text)
async def get_user_agreement(message: types.Message):
    await message.reply('Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-07-13-5')

#___________Referral__&&__Subscription__Things___________
@dp.message_handler(lambda message: message.text.lower() == 'купить подписку' or message.text.lower() == '/subscribe')
async def buy_sub_first(message: types.Message):
    if await is_in_pay_sys(message.from_user.id):
        if await check_if_subed(message.from_user.id) and not await do_have_free_sub(message.from_user.id):
            await message.answer("Вы уже подписаны", reply_markup=keyb_for_subed)
        elif not await check_if_subed(message.from_user.id) and await do_have_free_sub(message.from_user.id):
            await message.answer("У вас есть бесплатная подписка, при покупке платной подписки она отменится. Если вы готовы продолжить,нажми на кнопку под сообщением", reply_markup=create_not_first_time_buying_kb(message.from_user.id))
        else:
            await message.answer("Купите платную подписку нажав на одну из кнопок", reply_markup=create_not_first_time_buying_kb(message.from_user.id))
    else:
        if await do_have_free_sub(message.from_user.id):
            await message.answer('У вас есть бесплатная подписка. Если купите платную подписку, то она отменится. Если вы готовы так сделать, то нажмите на кнопку под сообщением', reply_markup=create_buying_link(message.from_user.id))
        else:
            await message.answer("Купите платную подписку нажав на одну из кнопок", reply_markup=create_buying_link(message.from_user.id))
# @dp.callback_query_handler()
# async def cancel_subscription(callback: types.CallbackQuery):
#     if callback.data == 'cancel_sub':
#         cancel_sub(int(callback.from_user.id))
#         count_money_attracted_by_one(callback.from_user.id)
#         await callback.answer('Вы успешно отписались ✅', reply_markup=keyb_for_unsubed)

# @dp.callback_query_handler()
# async def handle_callbacks(callback_query: types.CallbackQuery):
#     if callback_query.data == 'cancel_sub':
#         await cancel_sub(int(callback_query.from_user.id))
#         await count_money_attracted_by_one(callback_query.from_user.id)
#         await callback_query.message.answer('Вы успешно отписались ✅', reply_markup=keyb_for_unsubed)


@dp.message_handler(commands=['ref'])
async def get_yo_ref_data(message: types.Message):
    user_exists = await db.user_exists(message.from_user.id)
    if user_exists:
        if await is_in_pay_sys(message.from_user.id):
            if await check_if_subed(message.from_user.id) and not await do_have_free_sub(message.from_user.id):
                ref_traffic = await db.get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽", reply_markup=keyb_for_subed)
            elif not await check_if_subed(message.from_user.id) and await do_have_free_sub(message.from_user.id):
                ref_traffic = await db.get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽", reply_markup=keyb_for_subed)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
        else:
            if await do_have_free_sub(message.from_user.id):
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽", reply_markup=keyb_for_subed)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        await db.add_user(message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)

@dp.message_handler(lambda message: '✅ Подписка' == message.text or message.text.lower() == '/profile')
async def get_profile_data(message: types.Message):
    user_exists = await db.user_exists(message.from_user.id)
    if user_exists:
        if await is_in_pay_sys(message.from_user.id):
            if await check_if_subed(message.from_user.id):
                #ref_traffic = db.get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твой ID: {message.from_user.id}\n"+ f"\nУ вас есть еще {await get_sub_end(message.from_user.id)} оплаченных дней. \n\nНе пугайтесь если вы отменяли подписку, с вас не снимутся средства, просто у вас еще осталось несколько оплаченных дней после истечения которых вы потеряете доступ к полному функционалу бота!", reply_markup=create_cancel_kb(message.from_user.id))
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
        await db.add_user(message.from_user.id)
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
            "/check_referal -  посмотреть статистику реферала \n" +
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
        if await check_if_subed(int(message.text)) and await is_in_pay_sys(int(message.text)):
            await state.finish()
            await message.answer("Этот пользователь имеет подписку оформленную через cloud payments")
        elif not await check_if_subed(int(message.text)) and await is_in_pay_sys(int(message.text)):
            await state.update_data(user_id = message.text)
            await message.answer("Теперь надо ввести число дней на которое будет оформлена бесплатная подписка")
            await state.set_state(GiveFreeSub.SET_TIME_FOR_SUB)
        else:
            await state.update_data(user_id = message.text)
            await message.answer("Теперь надо ввести число дней на которое будет оформлена бесплатная подписка")
            await state.set_state(GiveFreeSub.SET_TIME_FOR_SUB)

    else:
        await state.finish()
        await message.answer("Вы прислали не число. Начните заново вызвав /free_sub")
    await ()

@dp.message_handler(state=GiveFreeSub.SET_TIME_FOR_SUB)
async def give_free_sub_step_choose_time(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            user_id = data['user_id']
            try:
                await state.finish()
                await bot.send_message(user_id, f'Вам выдана бесплатная подписка на {message.text} дней')
                await db.set_free_sub_end(user_id, datetime.now() + timedelta(days=int(message.text)))
                await message.answer(f'Бесплатная подписка на {message.text} дней выдана пользователю и он об этом уведомление')

            except:
                await state.finish()
                await message.answer("Возникла проблема при отправке уведомления пользователю. Он мог заблокировать бота")
    else:
        await state.finish()
        await message.answer("Вы прислали не число. Начните заново вызвав /free_sub")

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
        users_with_free = await get_users_with_free_sub()
        for user_id in users_with_free:
            free_sub = await db.get_free_sub_end(int(user_id))
            if free_sub is not None:
                free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
                free_sub = free_sub + timedelta(days=int(message.text))
                await db.set_free_sub_end(int(user_id), free_sub)
    else:
        await state.reset_state()
        await message.answer('Вы должны были ввести число')

@dp.message_handler(state= ExtendFreeSub.CHOOSE_ID)
async def extend_free_sub_id(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if await is_in_pay_sys(message.text) and not await check_if_subed(int(message.text)):
            if await do_have_free_sub(int(message.text)):
                await state.update_data(user_id = message.text)
                await message.answer('Теперь надо ввести число дней на которое вы хотите продлить бесплатную подписку пользователю')
                await state.set_state(ExtendFreeSub.SET_TIME)
            else:
                await state.finish()
                await message.answer("У человека нет бесплатной подписки")
        elif not await is_in_pay_sys(int(message.text)) and await do_have_free_sub(int(message.text)):
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
        free_sub = await db.get_free_sub_end(user_id)
        if free_sub is not None:
            free_sub = datetime.strptime(free_sub, '%Y-%m-%d %H:%M:%S.%f')
            free_sub = free_sub + timedelta(days=int(message.text))
            try:
                await state.finish()
                await bot.send_message(user_id, "Вам была продлена бесплатная подписка")
                await message.answer("Бесплатная подписка для пользователя продлена")
                await db.set_free_sub_end(user_id, free_sub)
            except:
                await state.finish()
                await message.answer("Что-то пошло не так на стороне пользователя")
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
        await update_sub_for_all(days=int(message.text))
        await state.finish()
        await message.answer("Платная подписка успешно продлена всем пользователям")
    else:
        await state.reset_state()
        await message.answer('Вы ввели не число. Начните заново вызвав команду /extend_sub')

@dp.message_handler(state=ExtendSub.CHOOSE_ID)
async def extend_sub_id(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if await is_in_pay_sys(int(message.text)):
            if await check_if_subed(int(message.text)):
                if await do_have_free_sub(int(message.text)) == False:
                    await state.update_data(user_id = message.text)
                    await message.answer('Теперь надо ввести число дней на которое вы хотите продлить платную подписку пользователю')
                    await state.set_state(ExtendSub.SET_EXTEND_TIME_O)
                else:
                    await state.reset_state()
                    await message.answer("У этого пользователя есть бесплатная подписка, вы не можете продлить ему платную без его предварительного согласия, он должен купить ее сам. \n  Начните заново вызвав команду /extend_sub")
            else: 
                await state.reset_state()    
                await message.answer("Этот пользователь не имеет платной подписки.  Начните заново вызвав команду /extend_sub") 
        else:
            await state.reset_state()
            await message.answer("Этот пользователь ни разу не оплачивал подписку.  Начните заново вызвав команду /extend_sub")
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
            await state.finish()
            await bot.send_message(user_id, f'Вам продлена платная подписка на {message.text} дней')
            await update_sub(user_id, days=int(message.text))
            await message.answer("Подписка успешно продлена и пользователь об этом уведомлен")
        except:
            await state.finish()
            await message.answer('До человека не дошло сообщения тк он заблокировал бота') 
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
        is_partner = await db.is_partner(int(message.text))
        if is_partner:
            await state.finish()
            await message.answer("Этот человек уже партнер")
            return
        if await check_if_subed(int(message.text)) or await do_have_free_sub(int(message.text)):
            try:
                await state.finish()
                await bot.send_message(message.text, 'Вам просвоен статус партнера')
                await message.answer("Вы присвоили человеку статус партнера и он об этом уведомлен")
                await db.set_partner(int(message.text))
            except:
                await state.finish()
                await message.answer('До человека не дошло сообщения тк он заблокировал бота') 
        else:
            await state.reset_state()
            await message.answer("Человек которому вы хотите присвоить статус партнерта не подписан на бота!")
    else:
        await state.reset_state()
        await message.answer('Повторите все заново вызвав команду /make_partner. Вы ввели не число!')

@dp.message_handler(commands=['check_referal'])
async def check_ref(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(CheckRef.CHOOSE_ID)
        await message.answer('Вам нужно ввести ID реферала статистику которого вы хотите проверить. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot')
    else:
        await message.answer("Вы не админ")

@dp.message_handler(state=CheckRef.CHOOSE_ID)
async def get_stat(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        ref_traffic = await db.get_referer_traffic(message.from_user.id) # кол-во людей
        await message.answer(f"Реферальная ссылка пользователя: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽")
    else:
        await state.reset_state()
        await message.answer('Вы неправильно ввели данные. введите только id. Вызовите команду /check_ref снова чтобы повторить процесс')

#_____АСИНХРОННЫЕ__ФУНКЦИИ__ДЛЯ__ВЫПОЛНЕНИЯ__ОСНОВНОГО__ФУНКЦИОНАЛА
async def process_stock(stock, volume_avg_prev, coef):
    while True:
        #await collecting_avg_event.wait()
        start_time = datetime.now(offset).replace(hour=9, minute=50, second=0, microsecond=0).time()
        end_time = datetime.now(offset).replace(hour=23, minute=50, second=0, microsecond=0).time()
        if end_time >= datetime.now(offset).time() and datetime.now(offset).time() >= start_time and datetime.now(offset).weekday() < 5:
            try:
                current_date = (datetime.now(offset)).strftime('%Y-%m-%d')
                current_hour = ("0" +str(datetime.now(offset).hour) if len(str(datetime.now(offset).hour)) < 2 else str(datetime.now(offset).hour))
                current_minute = ("0" +str(datetime.now(offset).minute - 1) if len(str(datetime.now(offset).minute - 1)) < 2 else str(datetime.now(offset).minute - 1))
                current_time = str(current_hour) +":"+ str(current_minute)
                stock_data = await get_stock_data(stock[0])
                current_stock_data = await get_current_stock_volume(stock[0], current_time)
                price_change = await get_price_change(current_stock_data[0], current_stock_data[1])
                sec_id = stock_data[0]
                print('Акция - ', sec_id)
                #volume_rub = current_stock_data[4]
                print('Объем - ', current_stock_data)
                print('price change - ', price_change)
                print('_________')


            except exceptions.RetryAfter as e:
                time.sleep(e.timeout)
            except Exception as e:
                print(e)
        else:
            print(f'Торги не идут {stock[0]}')
        await asyncio.sleep(60) 

async def process_stocks():
    #await collecting_avg_event.wait() 
    securities = await get_securities()

    # check if stock[0] in csv
    async with aiofiles.open('shares_v2.csv', mode='r') as reader:
        async for row in aiocsv.AsyncDictReader(reader, delimiter='\n'):
            if row is not None:
                for stock in securities:
                    if row['Полное название акций,тикет,сокращённое название,ликвидность'] is not None:
                        if row['Полное название акций,тикет,сокращённое название,ликвидность'].split(',')[1] == stock[0]:
                            coef = int(row['Полное название акций,тикет,сокращённое название,ликвидность'].split(',')[-1])
                            task = process_stock(stock, volumes_avg_prev, coef)
                            tasks.append(task)
            
        #task = asyncio.create_task(process_stock(stock, volumes_avg_prev))
    for task in tasks:
        asyncio.create_task(task)
        await asyncio.sleep(1)
        
         

async def main():
    await process_stocks()

async def delivery():
    users = await get_unsubed_users()
    if users:
        for user_id in users:
            await bot.send_message(user_id, 'У тебя нет подписки на нашего бота, советуем тебе оформить ее как можно скорее и приглашать своих друзей сюда. Вызови /subscribe')

async def collect_volumes_avg():
    global volumes_avg_prev
    collecting_avg_event.clear() 
    if datetime.now(offset).weekday() < 5:
        volumes_avg_prev = await get_prev_avg_months(volumes_avg_prev, 3)
        collecting_avg_event.set() 
        return volumes_avg_prev
    else:
        collecting_avg_event.set() 
        return {}

async def schedule_collecting_volumes():
    await collect_volumes_avg()

async def scheduler():
    aioschedule.every(1).days.at('01:00').do(collect_volumes_avg)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(db.connect())
    #asyncio.create_task(collect_volumes_avg())
    asyncio.create_task(main())
    asyncio.create_task(scheduler())



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)