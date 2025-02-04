import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Логирование
logging.basicConfig(level=logging.INFO)

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Кнопка "Все объявления" с ссылкой
    item1 = InlineKeyboardButton("Все объявления", url="https://zastroyschiki39.ru/flats")
    
    # Кнопка "Новости недвижимости"
    item2 = InlineKeyboardButton("Новости недвижимости", url="https://zastroyschiki39.ru/read")
    
    markup.add(item1, item2)
    await message.reply("Привет! Чем могу помочь?", reply_markup=markup)

# 🔹 Новый обработчик для получения Chat ID 🔹
@dp.message_handler(content_types=types.ContentType.TEXT)
async def get_chat_id(message: types.Message):
    await message.answer(f"Chat ID этой беседы: {message.chat.id}")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
