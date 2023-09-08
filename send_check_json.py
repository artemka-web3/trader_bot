import json
import aiofiles

async def read_trxs():
    async with aiofiles.open("payments.json", mode='r', encoding="utf-8") as file:
        json_data = await file.read()
        data = json.loads(json_data)
        return data

async def write_trxs(data):
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    async with aiofiles.open('payments.json', mode='w', encoding="utf-8") as file:
        await file.write(json_data)

async def clear_trxs():
    await write_trxs([])