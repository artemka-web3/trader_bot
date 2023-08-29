from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
from aiogram.types import ParseMode
from datetime import datetime, timedelta
from config import *
from pytz import timezone
from kb import *
from fsm import *
from moex_async import *
from aiocp_db import *
from aiodb import *
from collect_avg_volumes import *
from volumes_json import *
import asyncio
import aioschedule
import logging
import time
import datetime as dt


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

    if await is_in_pay_sys(message.from_user.id) and await check_if_subed(message.from_user.id):
        with open('intro.jpg', 'rb') as photo:
            await bot.send_photo(message.from_user.id, photo, """<b>"Радар биржи"</b> анализирует все минутные свечи акций торгуемых на Московской бирже. Если бот видит повышенный обьем в акции, то он сразу сигнализирует об этом.\n\n<b>Бот уведомляет:</b>\n\n🔸 Какой обьем был куплен.\n🔸 Изменение цены на данном обьеме.\n🔸 Изменение цены за день.\n🔸 О количестве покупателей и продавцов на данном обьеме.\n\n<b>Этот инструмент должен быть у каждого инвестора!</b>""", reply_markup=keyb_for_subed, parse_mode=ParseMode.HTML)
    else:
        with open('intro.jpg', 'rb') as photo:
            await bot.send_photo(message.from_user.id, photo, """<b>"Радар биржи"</b> анализирует все минутные свечи акций торгуемых на Московской бирже. Если бот видит повышенный обьем в акции, то он сразу сигнализирует об этом.\n\n<b>Бот уведомляет:</b>\n\n🔸 Какой обьем был куплен.\n🔸 Изменение цены на данном обьеме.\n🔸 Изменение цены за день.\n🔸 О количестве покупателей и продавцов на данном обьеме.\n\<b>Этот инструмент должен быть у каждого инвестора!</b>""", reply_markup=keyb_for_unsubed, parse_mode=ParseMode.HTML)
@dp.message_handler(lambda message: "📋 Пользовательское соглашение" == message.text)
async def get_user_agreement(message: types.Message):
    await message.reply('Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-07-13-5', disable_web_page_preview=True)

#___________Referral__&&__Subscription__Things___________
@dp.message_handler(lambda message: message.text.lower() == 'купить подписку' or message.text.lower() == '/subscribe')
async def buy_sub_first(message: types.Message):
    user_exists = await if_user_exists(message.from_user.id)
    if user_exists:
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
    else:
        await add_user(user_id=message.from_user.id)
        await message.answer('Попробуйте еще раз. Вызовите /subscribe или напишите "Купить Подписку"')

@dp.message_handler(commands=['ref'])
async def get_yo_ref_data(message: types.Message):
    user_exists = await if_user_exists(message.from_user.id)
    if user_exists:
        if await is_in_pay_sys(message.from_user.id):
            if await check_if_subed(message.from_user.id) and not await do_have_free_sub(message.from_user.id):
                ref_traffic = await get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽", reply_markup=keyb_for_subed, disable_web_page_preview=True)
            elif not await check_if_subed(message.from_user.id) and await do_have_free_sub(message.from_user.id):
                ref_traffic = await get_referer_traffic(message.from_user.id) # кол-во людей
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽", reply_markup=keyb_for_subed, disable_web_page_preview=True)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
        else:
            if await do_have_free_sub(message.from_user.id):
                await message.answer(f"Твоя реферальная ссылка: https://t.me/{BOT_NICK}?start={message.from_user.id}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные вами юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽", reply_markup=keyb_for_subed, disable_web_page_preview=True)
            else:
                await message.answer("Вы не подписаны", reply_markup=keyb_for_unsubed)
    else:
        await add_user(user_id=message.from_user.id)
        await message.answer("Вы не были занесены в БД, но я это исправил, подпишитесь на бота чтоб выполнить эту команду!", reply_markup=keyb_for_unsubed)

@dp.message_handler(lambda message: '✅ Подписка' == message.text or message.text.lower() == '/profile')
async def get_profile_data(message: types.Message):
    user_exists = await if_user_exists(message.from_user.id)
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
        await add_user(user_id=message.from_user.id)
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
        await message.answer('Вам нужно ввести ID человека которому вы хотите дать бесплатную подписку. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot', disable_web_page_preview=True)
        await state.set_state(GiveFreeSub.CHOOSE_USER)
    else:
        await message.answer('Вы не админ!')
@dp.message_handler(state=GiveFreeSub.CHOOSE_USER)
async def give_free_sub_step_choose_user(message: types.Message, state: FSMContext):
    user_exists = await if_user_exists(int(message.text))
    if user_exists:
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
    else:
        await state.reset_state()
        await add_user(user_id=int(message.text))
        await message.answer("Пользователь с таким id не был добавлен в базу данных, но я это исправил. Начните заново вызвав /free_sub")
        

@dp.message_handler(state=GiveFreeSub.SET_TIME_FOR_SUB)
async def give_free_sub_step_choose_time(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            user_id = data['user_id']
            try:
                await state.finish()
                await bot.send_message(user_id, f'Вам выдана бесплатная подписка на {message.text} дней')
                await set_free_sub_end(user_id, datetime.now() + timedelta(days=int(message.text)))
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
        await message.answer('Введите ID пользователя которому хотите продлить бесплатную подписку. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot', disable_web_page_preview=True)
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
            free_sub = await get_free_sub_end(user_id)
            if free_sub is not None:
                free_sub = convert_strdate_to_date(free_sub)
                free_sub = free_sub + timedelta(days=int(message.text))
                await set_free_sub_end(int(user_id), free_sub)
    else:
        await state.reset_state()
        await message.answer('Вы должны были ввести число')

@dp.message_handler(state= ExtendFreeSub.CHOOSE_ID)
async def extend_free_sub_id(message: types.Message, state: FSMContext):
    user_exists = await if_user_exists(int(message.text))
    if user_exists:
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
    else:
        await state.reset_state()
        await add_user(user_id=int(message.text))
        await message.answer('Этого человека нет в бд. \nНачните заново с другим пользователем либо дайте подписку пользователю с которым вы работали сейчас вызвав команду /free_sub.')
        


@dp.message_handler(state= ExtendFreeSub.SET_TIME)
async def extend_free_sub_choose_date_for_one(message: types.Message, state: FSMContext):
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
                await bot.send_message(user_id, "Вам была продлена бесплатная подписка")
                await message.answer("Бесплатная подписка для пользователя продлена")
                await set_free_sub_end(user_id, free_sub)
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
        await message.answer('Вам нужно ввести ID человека которому вы хотите продлить платную подписку. ID можно получить вот здесь отправив ссылку на профиль https://t.me/getmy_idbot', disable_web_page_preview=True)
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
    user_exists = await if_user_exists(int(message.text))
    if user_exists:
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
    else:
        await state.reset_state()
        await add_user(user_id=int(message.text))
        await message.answer('Этого человека нет в бд. \nНачните заново с другим пользователем вызвав /extend_sub')
        


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
        await message.answer('Вам нужно ввести ID человека которому вы хотите присвоить статус партнера. ID можно получить вот здесь отправив ссылку н профиль https://t.me/getmy_idbot', disable_web_page_preview=True)
    else:
        await message.answer("Вы не админ")

@dp.message_handler(state=MakePartner.CHOOSE_ID)
async def make_partner_id(message: types.Message, state: FSMContext):
    user_exists = await if_user_exists(int(message.text))
    if user_exists:
        if message.text.isdigit():
            this_is_partner = await is_partner(int(message.text))
            if this_is_partner:
                await state.finish()
                await message.answer("Этот человек уже партнер")
                return
            #if await check_if_subed(int(message.text)) or await do_have_free_sub(int(message.text)):
            try:
                await state.finish()
                await bot.send_message(message.text, 'Вам просвоен статус партнера')
                await message.answer("Вы присвоили человеку статус партнера и он об этом уведомлен")
                await set_partner(int(message.text))
            except:
                await state.finish()
                await message.answer('До человека не дошло сообщения тк он заблокировал бота') 
            #else:
            #    await state.reset_state()
            #    await message.answer("Человек которому вы хотите присвоить статус партнерта не подписан на бота!")
        else:
            await state.reset_state()
            await message.answer('Повторите все заново вызвав команду /make_partner. Вы ввели не число!')
    else:
        await state.reset_state()
        await add_user(user_id=int(message.text))
        await message.answer('Этого человека нет в бд. Я добавил его в базу данных \nТеперь начните заново вызвав /make_partner')



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
        ref_traffic = await get_referer_traffic(int(message.text)) # кол-во людей
        await message.answer(f"Реферальная ссылка пользователя: https://t.me/{BOT_NICK}?start={message.text}\n" + f"Кол-во привлеченных пользователей: {ref_traffic}\nКол-во денег, которые заплатили приглашенные юзеры: {await count_money_attracted_by_ref(message.from_user.id)}₽")
        await state.reset_state()
    else:
        await state.reset_state()
        await message.answer('Вы неправильно ввели данные. введите только id. Вызовите команду /check_ref снова чтобы повторить процесс')

#_____АСИНХРОННЫЕ__ФУНКЦИИ__ДЛЯ__ВЫПОЛНЕНИЯ__ОСНОВНОГО__ФУНКЦИОНАЛА        

# # async def delivery():
# #     users = await get_unsubed_users()
# #     if users:
# #         for user_id in users:
# #             await bot.send_message(user_id, 'У тебя нет подписки на нашего бота, советуем тебе оформить ее как можно скорее и приглашать своих друзей сюда. Вызови /subscribe')

async def send():
    data = await read_json()
    users = await get_all_users()
    logging.info('send')
    if data != []:
        for item in data:
            for user in users:
                if await check_if_subed(user[0]) or await do_have_free_sub(user[0]) or await if_sub_didnt_end(user[0]):
                    try:
                        await bot.send_message(
                            int(user[0]),
                            f"#{item['sec_id']} <b>{item['sec_name']}</b>\n\n{item['dir']}Аномальный объем\n"+
                            f"Изменение цены: {item['price_change']}%\n"+
                            f"Объем: {round(float(item['volume_rub'])/1000000, 2)}M₽ ({item['lot_amount']} лотов)\n" + 
                            (f"<b>Покупка: {item['buyers']}%</b> Продажа: {item['sellers']}%\n" if item['buyers'] > item['sellers'] else f"Покупка: {item['buyers']}% <b>Продажа: {item['sellers']}%</b>\n") +
                            f"Время: {item['current_date']} {item['time']}\n"+
                            f"Цена: {item['current_price']}₽\n"+ 
                            f"Изменение за день: {item['day_change']}%\n\n"+
                            "<b>Заметил Радар Биржи</b>\n"
                            f"""<b>Подключить <a href="https://t.me/{BOT_NICK}?start={user[0]}">@{BOT_NICK}</a></b>""",
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

def schedule_tasks():
    aioschedule.every(30).seconds.do(send)
    #aioschedule.every(1).seconds.do(collecting_avg)
    aioschedule.every().day.at('01:00').do(collecting_avg)


async def main():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    schedule_tasks()
    #asyncio.create_task(collecting_avg())
    asyncio.create_task(main())



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)




# ERRORS
# :Unclosed client session
# Forbidden: bot was blocked by the user