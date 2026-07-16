import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

load_dotenv()

async def main():
    session = AiohttpSession(
        proxy="http://127.0.0.1:10809"
    )

    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        session=session
    )

    me = await bot.get_me()
    print(me)

asyncio.run(main())