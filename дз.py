import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time

API_TOKEN = '7434325456:AAFwcudQz9TT6zTlXQe5iTNnWP9WC-JyTDM'

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

scheduler = AsyncIOScheduler()

reminders = {}

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для напоминаний. Используйте команду /help для получения списка доступных команд.")

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.answer("""
    Команды:
    /start - запуск бота
    /setreminder <время> <сообщение> - установить напоминание
    /listreminders - показать все напоминания
    /deletereminder <номер> - удалить напоминание
    /clearreminders - очистить все напоминания
    """)

@dp.message_handler(commands=['setreminder'])
async def set_reminder(message: types.Message):
    try:
        # Parse the message to get the time and message content
        parts = message.text.split(" ", 2)
        time_str = parts[1]
        reminder_message = parts[2]
        
        # Save reminder with a unique ID
        reminder_id = len(reminders) + 1
        reminders[reminder_id] = {'time': time_str, 'message': reminder_message}
        
        # Schedule reminder
        reminder_time = time.strptime(time_str, "%H:%M")
        trigger_time = time.mktime(reminder_time)
        scheduler.add_job(send_reminder, IntervalTrigger(start_date=trigger_time), args=[message.chat.id, reminder_message])
        
        await message.answer(f"Напоминание установлено! Я напомню вам в {time_str}: {reminder_message}")
    except Exception as e:
        await message.answer("Произошла ошибка. Убедитесь, что вы ввели команду в правильном формате.")

async def send_reminder(chat_id, message):
    await bot.send_message(chat_id, f"Напоминание: {message}")

@dp.message_handler(commands=['listreminders'])
async def list_reminders(message: types.Message):
    if reminders:
        reminders_list = "\n".join([f"{key}. {reminders[key]['time']} - {reminders[key]['message']}" for key in reminders])
        await message.answer(f"Ваши напоминания:\n{reminders_list}")
    else:
        await message.answer("У вас нет напоминаний.")

@dp.message_handler(commands=['deletereminder'])
async def delete_reminder(message: types.Message):
    try:
        reminder_id = int(message.text.split(" ")[1])
        if reminder_id in reminders:
            del reminders[reminder_id]
            await message.answer(f"Напоминание {reminder_id} удалено.")
        else:
            await message.answer("Напоминание с таким номером не найдено.")
    except Exception as e:
        await message.answer("Произошла ошибка.")

@dp.message_handler(commands=['clearreminders'])
async def clear_reminders(message: types.Message):
    reminders.clear()
    await message.answer("Все напоминания удалены.")

if __name__ == '__main__':
    scheduler.start()
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)