import apis.moex_async as moex_async
import asyncio
import json
import csv

volumes = {}
async def make():
    return await moex_async.get_prev_avg_months(volumes_dict=volumes, months_to_scroll=3)

async def to_json():
    with open('dictionary.json', 'w') as json_file:
        json.dump([volumes], json_file, indent=4) 

async def to_csv():
    with open('dictionary.csv', 'w', newline='') as csv_file:
        fieldnames = ["акция", "среднее"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Записываем заголовок
        writer.writeheader()

        # Записываем данные из JSON в CSV
        for row in volumes:
            writer.writerow(row)

from openpyxl import Workbook

async def to_tab():
    # Создаем новый Excel-файл
    workbook = Workbook()
    sheet = workbook.active

    # Заголовки столбцов (первая строка)
    headers = ['Название акции', 'Средние за минуту', 'За 3 месяца']
    sheet.append(headers)

    # Данные из словаря
    await moex_async.get_prev_avg_months_for_table(volumes_dict=volumes, months_to_scroll=3)
    for stock_name, stock_info in volumes.items():
        try:
            row_data = [stock_name, stock_info['Средние за минуту'], stock_info['За 3 месяца']]
            print(row_data)
            sheet.append(row_data)
        except:
            print('skip')

    # Сохраняем файл
    workbook.save('акции.xlsx')

loop = asyncio.get_event_loop()
loop.run_until_complete(to_tab())
