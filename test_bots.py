#!/usr/bin/env python3
"""
Простой скрипт для проверки подключения ботов
"""

import asyncio
from bots.role_bot import PMBot, ClientBot, DeveloperBot
from config import PM_BOT_TOKEN, CLIENT_BOT_TOKEN, DEV_BOT_TOKEN, BOT_PERSONALITIES


async def test_bots():
    """Тестирует подключение всех ботов"""

    print("🔍 Проверка подключения ботов...\n")

    bots = {
        "PM Bot": PMBot(PM_BOT_TOKEN, BOT_PERSONALITIES["pm"]),
        "Client Bot": ClientBot(CLIENT_BOT_TOKEN, BOT_PERSONALITIES["client"]),
        "Developer Bot": DeveloperBot(DEV_BOT_TOKEN, BOT_PERSONALITIES["dev"])
    }

    all_ok = True

    for name, bot in bots.items():
        try:
            info = await bot.get_me()
            if info:
                print(f"✅ {name}")
                print(f"   Username: @{info.username}")
                print(f"   ID: {info.id}")
                print(f"   Name: {info.first_name}")
                print()
            else:
                print(f"❌ {name} - Не удалось получить информацию")
                all_ok = False
        except Exception as e:
            print(f"❌ {name} - Ошибка: {e}")
            all_ok = False

    if all_ok:
        print("\n✅ Все боты подключены успешно!")
        print("\n📝 Следующие шаги:")
        print("1. Создайте Telegram группу")
        print("2. Добавьте всех трех ботов в группу:")
        for name, bot in bots.items():
            info = await bot.get_me()
            if info:
                print(f"   - @{info.username}")
        print("3. Получите Chat ID группы (см. README.md)")
        print("4. Добавьте Chat ID в .env файл (TARGET_CHAT_ID)")
        print("5. Запустите: python3 main.py")
    else:
        print("\n❌ Не все боты подключены!")
        print("Проверьте токены в .env файле")

    return all_ok


if __name__ == "__main__":
    asyncio.run(test_bots())
