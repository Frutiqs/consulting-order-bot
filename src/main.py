from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN

# Создаем бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message):
    await message.reply("Привет! Я готов принимать заявки.")

# Асинхронная точка входа
async def main():
    print("Бот запущен...")
    await dp.start_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())