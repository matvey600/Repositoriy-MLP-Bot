from aiogram import Bot
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

async def test():
    bot = Bot(os.getenv("BOT_TOKEN"))
    me = await bot.get_me()
    print(me)

asyncio.run(test())