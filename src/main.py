from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Новая заявка", "Мои заказы")
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Обработка заявки
@dp.message_handler(text="Новая заявка")
async def new_request(message: types.Message):
    await message.answer("Введите описание задачи:")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)