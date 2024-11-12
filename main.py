import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
import os
import asyncio

API_TOKEN = '7442158907:AAGC7Gl7Inew3xKtq_1zaUbC3622SEgz0NU'

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для скачивания аудио
def download_audio(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(id)s.mp3',
        'ffmpeg_location': '/path/to/ffmpeg'  # Укажите полный путь к ffmpeg
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = f"{info_dict['id']}.mp3"
        return filename
    except Exception as e:
        logging.error(f"Ошибка при скачивании: {e}")
        return None

# Функция для скачивания видео
def download_video(url: str):
    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(id)s.mp4',
        'ffmpeg_location': '/path/to/ffmpeg'  # Укажите полный путь к ffmpeg
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = f"{info_dict['id']}.mp4"
        return filename
    except Exception as e:
        logging.error(f"Ошибка при скачивании: {e}")
        return None

# Обработчик команды /start
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправьте мне ссылку на видео с TikTok или YouTube, чтобы я мог скачать его для вас.")

# Обработчик для кнопок выбора типа загрузки
async def process_link(message: types.Message):
    url = message.text

    # Проверка ссылки
    if "tiktok.com" in url or "youtube.com" in url or "youtu.be" in url:
        # Клавиатура с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Скачать как MP3", callback_data=f"audio|{url}")],
            [InlineKeyboardButton(text="Скачать видео", callback_data=f"video|{url}")]
        ])
        await message.reply("Выберите формат загрузки:", reply_markup=keyboard)
    else:
        await message.reply("Пожалуйста, отправьте корректную ссылку на видео с YouTube или TikTok.")

# Обработчик для обработки нажатия на кнопки
async def callback_query_handler(callback_query: CallbackQuery):
    data, url = callback_query.data.split('|')
    await callback_query.answer("Начинаю загрузку...")

    if data == "audio":
        filename = download_audio(url)
        if filename:
            file = FSInputFile(filename)
            await callback_query.message.reply_document(file)
            os.remove(filename)
        else:
            await callback_query.message.reply("Не удалось загрузить аудио. Попробуйте другую ссылку.")
    elif data == "video":
        filename = download_video(url)
        if filename:
            file = FSInputFile(filename)
            await callback_query.message.reply_video(file)
            os.remove(filename)
        else:
            await callback_query.message.reply("Не удалось загрузить видео. Попробуйте другую ссылку.")

# Регистрация обработчиков
dp.message.register(send_welcome, Command("start"))
dp.message.register(process_link)
dp.callback_query.register(callback_query_handler)

# Асинхронная функция для запуска бота
async def main():
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())
