import os
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

logging.basicConfig(level=logging.INFO)


def get_holiday(date_str: str = None) -> str:
    """Получает информацию о праздниках"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    try:
        year = date_str[:4]
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/RU"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        holidays = response.json()

        holidays_on_date = [h for h in holidays if h['date'] == date_str]

        if holidays_on_date:
            holiday_names = [h['localName'] for h in holidays_on_date]
            return f"<b>{date_str}</b>\n\nПраздник: {', '.join(holiday_names)}"
        else:
            return f"<b>{date_str}</b>\n\nНа эту дату государственных праздников в России нет."

    except requests.exceptions.RequestException:
        return "Не удалось получить данные о праздниках. Проверьте интернет."


def is_valid_date(date_string: str) -> bool:
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие по имени"""
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("Праздник сегодня", callback_data="today")],
        [InlineKeyboardButton("Проверить другую дату", callback_data="check")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Привет, {user_name}!\n\n"
        f"Я бот для поиска праздников в России.\n"
        f"Нажми /help для команд.",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    await update.message.reply_text(
        "Команды:\n"
        "/start - Приветствие\n"
        "/help - Помощь\n"
        "/today - Праздники сегодня\n\n"
        "Формат даты: ГГГГ-ММ-ДД\n"
        "Пример: 2025-01-01"
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Праздники сегодня"""
    holiday_info = get_holiday()
    await update.message.reply_text(holiday_info, parse_mode='HTML')


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос даты"""
    await update.message.reply_text(
        "Введите дату в формате ГГГГ-ММ-ДД:\nПример: 2025-01-01"
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()

    if query.data == "today":
        holiday_info = get_holiday()
        await query.message.reply_text(holiday_info, parse_mode='HTML')
    elif query.data == "check":
        await query.message.reply_text("Введите дату в формате ГГГГ-ММ-ДД")
    elif query.data == "help":
        await query.message.reply_text(
            "Просто отправь дату в формате ГГГГ-ММ-ДД\n"
            "или используй команды: /today, /check"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    text = update.message.text.strip()

    if is_valid_date(text):
        holiday_info = get_holiday(text)
        await update.message.reply_text(holiday_info, parse_mode='HTML')
    else:
        await update.message.reply_text(
            "Неверный формат!\n"
            "Используйте: ГГГГ-ММ-ДД\n"
            "Пример: 2025-01-01\n\n"
            "Или нажмите /today"
        )


def main():
    """Запуск бота"""
    print("Бот запускается...")
    print("Библиотека: python-telegram-bot 20.x")
    print("Вариант №1: Праздники в любой день года")

    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот готов к работе! Напишите @ваш_username_бота в Telegram")
    application.run_polling()


if __name__ == '__main__':
    main()