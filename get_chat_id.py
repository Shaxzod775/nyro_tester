#!/usr/bin/env python3
"""
Скрипт для получения Chat ID телеграм группы
"""

import asyncio
from telegram import Bot
from config import PM_BOT_TOKEN


async def get_chat_id():
    """Получает список последних обновлений и показывает Chat ID"""

    print("🔍 Поиск Chat ID...\n")
    print("📝 Инструкция:")
    print("1. Добавьте всех ботов в вашу Telegram группу")
    print("2. Отправьте любое сообщение в группу (например: 'Привет!')")
    print("3. Запустите этот скрипт\n")
    print("Ожидание обновлений...\n")

    bot = Bot(token=PM_BOT_TOKEN)

    try:
        # Получаем последние обновления
        updates = await bot.get_updates(limit=10)

        if not updates:
            print("❌ Обновлений не найдено!")
            print("\nВозможные причины:")
            print("1. Вы не отправили сообщение в группу")
            print("2. Боты не добавлены в группу")
            print("3. У ботов включен Privacy Mode (отключите через @BotFather)")
            return

        print(f"✅ Найдено обновлений: {len(updates)}\n")

        # Собираем уникальные чаты
        chats = {}
        for update in updates:
            if update.message and update.message.chat:
                chat = update.message.chat
                if chat.id not in chats:
                    chats[chat.id] = {
                        "id": chat.id,
                        "type": chat.type,
                        "title": chat.title or chat.first_name or "Unknown"
                    }

        if not chats:
            print("❌ Не найдено сообщений в группах!")
            print("\nПопробуйте:")
            print("1. Отправить сообщение в группу")
            print("2. Сделать ботов администраторами группы")
            print("3. Отключить Privacy Mode через @BotFather:")
            print("   /setprivacy -> выберите бота -> Disable")
            return

        print("📋 Найденные чаты:\n")
        for chat_id, chat_info in chats.items():
            print(f"Chat ID: {chat_id}")
            print(f"Type: {chat_info['type']}")
            print(f"Title: {chat_info['title']}")
            print("-" * 50)

        print("\n✅ Скопируйте Chat ID и добавьте в .env файл:")
        print(f"TARGET_CHAT_ID={list(chats.keys())[0]}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nПроверьте:")
        print("1. Токен бота в .env корректен")
        print("2. Бот добавлен в группу")
        print("3. У бота есть доступ к сообщениям")


if __name__ == "__main__":
    asyncio.run(get_chat_id())
