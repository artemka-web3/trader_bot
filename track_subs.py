from cloudpayments import CloudPayments
from db import *
from subs_json import *

client = CloudPayments('pk_c8695290fec5bcb40f468cca846d2', 'd3119d06f156dad88a2ed516957b065b')



async def track_paid_subscriptions():
    all_users = await get_all_users()
    print(1)
    for user in all_users:
        user_id = user[0]
        for sub in client.list_subscriptions(user_id):
            if sub.status == 'Cancelled':
                print(f"{sub.account_id}", sub.start_date + timedelta(days=30))
                if sub.start_date + timedelta(days=30) > datetime.now(offset):
                    await set_paid_sub_end(user[0], sub.start_date + timedelta(days=30))
                elif not await do_have_paid_sub(user[0]):
                    notifications = list(get_notifications())
                    is_receiver_present = any(item["receiver"] == user[0] for item in notifications)
                    if not is_receiver_present:
                        notification = {
                            "receiver": user[0],
                            "message": "Ваша платная подписка закончилась! Чтобы получать объемы от бота, активируйте ее еще раз!"
                        }
                        notifications.append(notification)
                        write_notifications(notifications)  
                elif sub.start_date + timedelta(days=30) <= datetime.now(offset): 
                    notifications = list(get_notifications())
                    is_receiver_present = any(item["receiver"] == user[0] for item in notifications)
                    if not is_receiver_present:
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
                is_receiver_present = any(item["receiver"] == user[0] for item in notifications)
                if not is_receiver_present:
                    notification = {
                        "receiver": user[0],
                        "message": "Ваша бесплатная подписка закончилась!"
                    }
                    notifications.append(notification)
                    await set_free_sub_end(user[0], None)
                    write_notifications(notifications)

async def track_all_subs():
    #print(await get_subed_users())
    #return await do_have_paid_sub(6132645711)
    await track_free_subscriptions()
    await asyncio.sleep(10)
    await track_paid_subscriptions()


# for i in client.list_subscriptions(1105549622):
#     print(i)
    
# loop = asyncio.get_event_loop()
# print(loop.run_until_complete(track_all_subs()))


