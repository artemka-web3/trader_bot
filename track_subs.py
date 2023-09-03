from cloudpayments import CloudPayments
from db import *
import json

client = CloudPayments('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')

def get_notifications():
    with open("notifications.json", mode='r', encoding="utf-8") as file:
        json_data = file.read()
        data = json.loads(json_data)
        return data

def write_notifications(data):
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    with open('notifications.json', mode='w', encoding="utf-8") as file:
        file.write(json_data)


async def track_paid_subscriptions():
    all_users = get_all_users()
    for user in all_users:
        user_id = user[0]
        for sub in client.list_subscriptions(user_id):
            if sub.status == 'Cancelled':
                if not await do_have_paid_sub(user[0]):
                    notification = {
                        "receiver": user[0],
                        "message": "Ваша платная подписка закончилась! Чтобы получать объемы от бота, активируйте ее еще раз!"
                    }
                    write_notifications(notification)
                # проверять start_date
                # если она больше чем дата в БД
                # то все окей
                # если нет
                # то идет отмена и уведомления (точнее добавление уведомления в json)
                # а после отправка из бота уже
            elif sub.status == 'Active':
                next_trx_date = sub.next_transaction_date
                if convert_strdate_to_date(await get_paid_sub_end(user[0])) < next_trx_date:
                    await set_paid_sub_end(user[0], next_trx_date)
                    await update_money_paid(user[0], sub.amount)

async def track_free_subscriptions():
    all_users = get_all_users()
    for user in all_users:
        user_id = user[0]
        if await get_free_sub_end(user_id):
            if not await do_have_free_sub(user_id):
                notification = {
                    "receiver": user[0],
                    "message": "Ваша бесплатная подписка закончилась!"
                }
                await set_free_sub_end(user[0], None)
                write_notifications(notification)

async def main():
    asyncio.create_task(track_free_subscriptions)
    asyncio.sleep(10)
    asyncio.create_task(track_paid_subscriptions)        

asyncio.run(main)
# for sub in client.list_subscriptions(1892710536):
#     print(sub)
