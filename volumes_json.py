import aiofiles
import json
import asyncio

# BIG VOLUMES
async def read_json():
    async with aiofiles.open("big_volumes.json", mode='r', encoding="utf-8") as file:
        json_data = await file.read()
        data = json.loads(json_data)
        return data

async def write_json(data):
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    async with aiofiles.open('big_volumes.json', mode='w', encoding="utf-8") as file:
        await file.write(json_data)

async def clear_json():
    await write_json([])

# AVG VOLUMES
async def read_json_file():
    async with aiofiles.open('volumes_avg_prev.json', mode="r", encoding='utf-8') as file:
        data = await file.read()
        return json.loads(data)

async def write_json_file(data):
    async with aiofiles.open('volumes_avg_prev.json', mode="w", encoding='utf-8') as file:
        await file.write(json.dumps(data, indent=4, ensure_ascii=False))

async def update_json_data(key, value):
    data = await read_json_file()
    data[key] = value
    await write_json_file(data)

# Асинхронная функция для очистки JSON-файла
async def clear_json_file():
    await write_json_file({})