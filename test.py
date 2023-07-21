import aiofiles
import aiocsv
import asyncio

async def main():
    async with aiofiles.open('shares_v2.csv', mode='r') as reader:
        async for row in aiocsv.AsyncDictReader(reader, delimiter='\n'):
            print(row)

asyncio.run(main())