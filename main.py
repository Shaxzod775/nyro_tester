#!/usr/bin/env python3
"""
Главная точка входа в систему AI-агентов для Telegram
"""

import asyncio
import sys
from coordinator import Coordinator
from config import TARGET_CHAT_ID


def print_banner():
    """Выводит красивый баннер"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🤖 AI Telegram Bots Orchestrator 🤖             ║
║                                                           ║
║  Система для симуляции рабочих диалогов в Telegram       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Выводит меню команд"""
    menu = """
📋 ДОСТУПНЫЕ КОМАНДЫ:

1. run     - Запустить полный цикл (генерация + выполнение)
2. generate - Только сгенерировать сценарий
3. show    - Показать текущий сценарий
4. execute - Выполнить текущий сценарий
5. check   - Проверить состояние ботов
6. help    - Показать это меню
7. exit    - Выход

Введите номер команды или её название:
    """
    print(menu)


async def interactive_mode():
    """Интерактивный режим работы"""
    
    print_banner()
    
    # Инициализируем координатор
    coordinator = Coordinator()
    
    # Проверяем ботов при запуске
    print("\n🔍 Выполняем первоначальную проверку...")
    bots_ok = await coordinator.check_bots()
    
    if not bots_ok:
        print("\n⚠️  ВНИМАНИЕ: Не все боты доступны!")
        print("Проверьте токены в файле .env или config.py")
        response = input("\nПродолжить? (y/n): ")
        if response.lower() != 'y':
            return
    
    print(f"\n💬 Target Chat ID: {TARGET_CHAT_ID}")
    if TARGET_CHAT_ID == "your_chat_id_here":
        print("⚠️  Не забудьте установить TARGET_CHAT_ID в config.py!")
    
    print_menu()
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command in ['1', 'run']:
                print("\n" + "="*60)
                prompt = input("📝 Введите описание сценария: ").strip()
                if not prompt:
                    print("❌ Описание не может быть пустым!")
                    continue
                
                num_messages = input("📊 Количество сообщений (Enter для авто): ").strip()
                num_messages = int(num_messages) if num_messages else None
                
                chat_id = input(f"💬 Chat ID (Enter для {TARGET_CHAT_ID}): ").strip()
                chat_id = int(chat_id) if chat_id else TARGET_CHAT_ID
                
                print("\n🚀 Запускаем полный цикл...\n")
                await coordinator.run_full_cycle(prompt, chat_id, num_messages)
            
            elif command in ['2', 'generate']:
                print("\n" + "="*60)
                prompt = input("📝 Введите описание сценария: ").strip()
                if not prompt:
                    print("❌ Описание не может быть пустым!")
                    continue
                
                num_messages = input("📊 Количество сообщений (Enter для авто): ").strip()
                num_messages = int(num_messages) if num_messages else None
                
                scenario = coordinator.generate_scenario(prompt, num_messages)
                print("\n✅ Сценарий сгенерирован!")
                
                show = input("\nПоказать сценарий? (y/n): ").strip().lower()
                if show == 'y':
                    coordinator.print_scenario(scenario)
            
            elif command in ['3', 'show']:
                coordinator.print_scenario()
            
            elif command in ['4', 'execute']:
                if coordinator.current_scenario is None:
                    print("❌ Нет сценария для выполнения! Сначала сгенерируйте сценарий.")
                    continue
                
                chat_id = input(f"💬 Chat ID (Enter для {TARGET_CHAT_ID}): ").strip()
                chat_id = int(chat_id) if chat_id else TARGET_CHAT_ID
                
                print("\n▶️  Выполняем сценарий...\n")
                await coordinator.execute_scenario(chat_id)
            
            elif command in ['5', 'check']:
                await coordinator.check_bots()
            
            elif command in ['6', 'help']:
                print_menu()
            
            elif command in ['7', 'exit', 'quit', 'q']:
                print("\n👋 До свидания!")
                break
            
            else:
                print(f"❌ Неизвестная команда: {command}")
                print("Введите 'help' для списка команд")
        
        except KeyboardInterrupt:
            print("\n\n👋 Прервано пользователем. До свидания!")
            break
        
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            print("Попробуйте снова или введите 'help'")


async def quick_run_mode():
    """Быстрый запуск с параметрами по умолчанию"""
    
    print_banner()
    print("\n🚀 БЫСТРЫЙ ЗАПУСК\n")
    
    coordinator = Coordinator()
    
    # Дефолтный сценарий
    default_prompt = "Создай диалог про разработку веб-сайта для ресторана с онлайн-заказом"
    
    await coordinator.run_full_cycle(
        user_prompt=default_prompt,
        num_messages=25
    )


def main():
    """Главная функция"""
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--quick', '-q']:
            # Быстрый запуск
            asyncio.run(quick_run_mode())
        elif sys.argv[1] in ['--help', '-h']:
            print("Использование:")
            print("  python main.py           - Интерактивный режим")
            print("  python main.py --quick   - Быстрый запуск с дефолтным сценарием")
            print("  python main.py --help    - Показать эту справку")
        else:
            print(f"Неизвестный аргумент: {sys.argv[1]}")
            print("Используйте --help для справки")
    else:
        # Интерактивный режим
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()