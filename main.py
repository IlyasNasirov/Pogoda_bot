import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers import router
from models import init_db
from notify_weather import send_notifications
from sessions import clear_expired_sessions

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN,
          default=DefaultBotProperties(parse_mode="Markdown"))


async def main():
    await init_db()
    asyncio.create_task(send_notifications(bot))
    asyncio.create_task(clear_expired_sessions())
    dp = Dispatcher()
    dp.include_router(router)
    print("Pogoda is running...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
