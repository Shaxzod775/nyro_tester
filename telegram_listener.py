"""
Telegram Listener - Слушает все сообщения из групп, в которые добавлен бот
Печатает все сообщения с информацией о chat_id
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import DEV_BOT_TOKEN, PM_BOT_TOKEN, CLIENT_BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех сообщений"""
    message = update.message
    
    if message is None:
        return
    
    # Получаем информацию о чате
    chat = message.chat
    chat_id = chat.id
    chat_type = chat.type
    chat_title = chat.title if chat.title else "Личный чат"
    chat_username = chat.username if chat.username else "Нет username"
    
    # Получаем информацию об отправителе
    user = message.from_user
    user_id = user.id if user else "Неизвестно"
    user_name = user.full_name if user else "Неизвестно"
    user_username = user.username if user else "Нет username"
    
    # Текст сообщения
    text = message.text if message.text else "Нет текста (медиа/стикер/другое)"
    
    # Печатаем информацию
    print("\n" + "="*80)
    print(f"📨 НОВОЕ СООБЩЕНИЕ")
    print("="*80)
    print(f"🆔 CHAT ID: {chat_id}")
    print(f"📋 Тип чата: {chat_type}")
    print(f"💬 Название чата: {chat_title}")
    print(f"🔗 Username чата: @{chat_username}")
    print(f"👤 Отправитель ID: {user_id}")
    print(f"👤 Имя отправителя: {user_name}")
    print(f"🔗 Username отправителя: @{user_username}")
    print(f"📝 Текст сообщения: {text}")
    print(f"🕐 Время: {message.date}")
    print("="*80 + "\n")
    
    # Логируем в файл (опционально)
    logger.info(f"Chat ID: {chat_id} | Chat: {chat_title} | User: {user_name} | Text: {text[:100]}")


async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отредактированных сообщений"""
    message = update.edited_message
    
    if message is None:
        return
    
    chat = message.chat
    chat_id = chat.id
    chat_title = chat.title if chat.title else "Личный чат"
    
    user = message.from_user
    user_name = user.full_name if user else "Неизвестно"
    text = message.text if message.text else "Нет текста"
    
    print("\n" + "="*80)
    print(f"✏️ ОТРЕДАКТИРОВАННОЕ СООБЩЕНИЕ")
    print("="*80)
    print(f"🆔 CHAT ID: {chat_id}")
    print(f"💬 Название чата: {chat_title}")
    print(f"👤 Отправитель: {user_name}")
    print(f"📝 Новый текст: {text}")
    print("="*80 + "\n")


def main():
    """Главная функция"""
    print("🤖 Telegram Listener запущен")
    print("📡 Слушаю сообщения из всех групп, в которые добавлен бот...")
    print("💡 Для остановки нажмите Ctrl+C\n")
    
    # Выбираем токен бота (можно изменить на PM_BOT_TOKEN или CLIENT_BOT_TOKEN)
    BOT_TOKEN = DEV_BOT_TOKEN
    
    if BOT_TOKEN == "your_dev_bot_token_here" or not BOT_TOKEN:
        print("❌ Ошибка: Токен бота не настроен!")
        print("💡 Убедитесь, что в .env файле указан DEV_BOT_TOKEN")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    application.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited_message))
    
    # Запускаем бота
    print(f"✅ Бот запущен и слушает обновления...\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Listener остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        logger.exception("Ошибка при работе listener")

