import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Логирование
logging.basicConfig(level=logging.INFO)

# Клавиатуры
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Начать"))
city_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Калининград"),
    KeyboardButton("Калининградская область"),
    KeyboardButton("Другой город")
)
role_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Физ лицо"),
    KeyboardButton("Юр лицо")
)
contact_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("В чате"),
    KeyboardButton("По телефону")
)
confirm_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Подождать звонка"),
    KeyboardButton("Позвонить сразу")
)

# Словарь для хранения данных пользователей
user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Добро пожаловать! Я могу помочь вам получить консультацию. Нажмите 'Начать', чтобы продолжить.", reply_markup=start_kb)

@dp.message_handler(lambda message: message.text == "Начать")
async def ask_city(message: types.Message):
    await message.answer("Из какого вы города?", reply_markup=city_kb)

@dp.message_handler(lambda message: message.text in ["Калининград", "Калининградская область", "Другой город"])
async def ask_role(message: types.Message):
    user_data[message.from_user.id] = {"city": message.text}
    await message.answer("Кем вы являетесь?", reply_markup=role_kb)

@dp.message_handler(lambda message: message.text in ["Физ лицо", "Юр лицо"])
async def ask_contact_method(message: types.Message):
    user_data[message.from_user.id]["role"] = message.text
    await message.answer("Как вам удобнее получить консультацию?", reply_markup=contact_kb)

@dp.message_handler(lambda message: message.text in ["В чате", "По телефону"])
async def ask_name(message: types.Message):
    user_data[message.from_user.id]["contact_method"] = message.text
    if user_data[message.from_user.id]["role"] == "Юр лицо":
        await message.answer("Напишите название вашей компании.")
    else:
        await message.answer("Как к вам обращаться?")

@dp.message_handler(lambda message: message.from_user.id in user_data and "name" not in user_data[message.from_user.id])
async def ask_query(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    await message.answer("Укажите ваш запрос или ситуацию, с которой вы обращаетесь.")

@dp.message_handler(lambda message: message.from_user.id in user_data and "query" not in user_data[message.from_user.id])
async def ask_phone(message: types.Message):
    user_data[message.from_user.id]["query"] = message.text
    if user_data[message.from_user.id]["contact_method"] == "По телефону":
        await message.answer("Напишите ваш номер телефона.")
    else:
        await confirm_contact(message)

@dp.message_handler(lambda message: message.from_user.id in user_data and "phone" not in user_data[message.from_user.id])
async def confirm_contact(message: types.Message):
    user_data[message.from_user.id]["phone"] = message.text
    user_info = user_data[message.from_user.id]
    phone = user_info["phone"] if user_info["contact_method"] == "По телефону" else "—"  # Если контакт через чат, ставим прочерк
    msg = (f"📢 Новый запрос на консультацию!\n\n"
           f"🏙 Город: {user_info['city']}\n"
           f"👤 Статус: {user_info['role']}\n"
           f"📞 Способ связи: {user_info['contact_method']}\n"
           f"📛 Имя/Компания: {user_info['name']}\n"
           f"📲 Телефон: {phone}\n"
           f"💬 Запрос: {user_info['query']}\n"
           f"🆔 User ID: {message.from_user.id}")

    if SUPPORT_GROUP_ID:
        await bot.send_message(SUPPORT_GROUP_ID, msg)

    if user_info["contact_method"] == "По телефону":
        await message.answer(
            "С вами свяжутся в ближайшее время. Если не хотите ждать, нажмите 'Позвонить сразу'",
            reply_markup=confirm_kb
        )
    else:
        await message.answer("Ожидайте, с вами свяжется оператор в чате.")

@dp.message_handler(lambda message: message.text in ["Подождать звонка", "Позвонить сразу"])
async def final_step(message: types.Message):
    user_info = user_data.get(message.from_user.id)
    if user_info and user_info["contact_method"] == "По телефону":
        if message.text == "Позвонить сразу":
            await message.answer("Позвоните нам по номеру: +7 (911) 458-39-39")
        else:
            await message.answer("Спасибо! Мы с вами свяжемся.")
    else:
        await message.answer("Ожидайте, с вами свяжется оператор в чате.")

@dp.message_handler(commands=['reply'])
async def reply_to_user(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Используйте формат: /reply user_id текст")
        return
    user_id = args[1]
    response_text = " ".join(args[2:])
    try:
        await bot.send_message(user_id, f"Ответ от оператора: {response_text}")
        await message.answer("Ответ отправлен пользователю.")
    except Exception as e:
        await message.answer(f"Ошибка при отправке: {e}")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
