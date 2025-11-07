#!/usr/bin/env python3
"""
Скрипт для запуска веб-сервера
"""

import uvicorn
import sys


def main():
    """Запускает FastAPI сервер"""

    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🌐 AI Telegram Bots Web Interface 🌐            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

🚀 Запуск веб-сервера...

📱 Веб-интерфейс: http://localhost:8000
📚 API документация: http://localhost:8000/docs
📊 Alternative API docs: http://localhost:8000/redoc

⚡ Сервер поддерживает hot-reload (автоматическая перезагрузка при изменении кода)

Нажмите Ctrl+C для остановки сервера
    """)

    try:
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Сервер остановлен")
        sys.exit(0)


if __name__ == "__main__":
    main()
