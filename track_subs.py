from cloudpayments import CloudPayments
from db import *
import json
import asyncio

client = CloudPayments('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')
# for sub in client.list_subscriptions(6554601918):
#     print(sub)
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
    all_users = await get_all_users()
    print(1)
    for user in all_users:
        user_id = user[0]
        for sub in client.list_subscriptions(user_id):
            if sub.status == 'Cancelled':
                if not await do_have_paid_sub(user[0]):
                    notifications = list(get_notifications())
                    notification = {
                        "receiver": user[0],
                        "message": "Ваша платная подписка закончилась! Чтобы получать объемы от бота, активируйте ее еще раз!"
                    }
                    notifications.append(notification)
                    write_notifications(notifications)
                # проверять start_date
                # если она больше чем дата в БД
                # то все окей
                # если нет
                # то идет отмена и уведомления (точнее добавление уведомления в json)
                # а после отправка из бота уже
            elif sub.status == 'Active':
                next_trx_date = sub.next_transaction_date
                if await get_paid_sub_end(user[0]):
                    if convert_strdate_to_date(await get_paid_sub_end(user[0])) < next_trx_date:
                        await set_paid_sub_end(user[0], next_trx_date)
                        await update_money_paid(user[0], sub.amount)
                else:
                    await set_paid_sub_end(user[0], next_trx_date)
                    await update_money_paid(user[0], sub.amount)


async def track_free_subscriptions():
    all_users = await get_all_users()
    print(2)
    for user in all_users:
        user_id = user[0]
        if await get_free_sub_end(user_id):
            if not await do_have_free_sub(user_id):
                notifications = list(get_notifications())
                notification = {
                    "receiver": user[0],
                    "message": "Ваша бесплатная подписка закончилась!"
                }
                notifications.append(notification)
                await set_free_sub_end(user[0], None)
                write_notifications(notifications)

async def main():
    await track_paid_subscriptions()
    await asyncio.sleep(10)
    await track_free_subscriptions()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


