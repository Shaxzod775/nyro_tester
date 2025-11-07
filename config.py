import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Tokens
PM_BOT_TOKEN = os.getenv("PM_BOT_TOKEN", "your_pm_bot_token_here")
CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN", "your_client_bot_token_here")
DEV_BOT_TOKEN = os.getenv("DEV_BOT_TOKEN", "your_dev_bot_token_here")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Telegram Group Chat ID (получите после создания группы и добавления ботов)
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID", "your_chat_id_here")

# AI Settings
MODEL_NAME = "gpt-5-mini"  # или "gpt-3.5-turbo" для экономии
MAX_MESSAGES = 50
MIN_MESSAGES = 30

# Bot Personalities
BOT_PERSONALITIES = {
    "pm": {
        "name": "Алексей (PM)",
        "role": "Project Manager",
        "personality": """Ты опытный проект-менеджер. Ты организованный, дружелюбный, 
        следишь за сроками и помогаешь команде. Пишешь структурированно, иногда используешь 
        эмодзи (📋, ✅, 👍). Ты связующее звено между клиентом и разработчиком."""
    },
    "client": {
        "name": "Мария (Заказчик)",
        "role": "Client",
        "personality": """Ты заказчик проекта. Ты деловая, знаешь чего хочешь, но иногда 
        задаешь уточняющие вопросы. Ценишь качество и сроки. Пишешь вежливо и по делу. 
        Иногда используешь эмодзи (😊, 👌)."""
    },
    "dev": {
        "name": "Дмитрий (Developer)",
        "role": "Developer",
        "personality": """Ты опытный разработчик. Ты технически подкован, задаешь 
        уточняющие вопросы по техническим деталям, предлагаешь решения. Пишешь четко 
        и конкретно. Иногда используешь технические термины и эмодзи (💻, 🔧, ✨)."""
    }
}

# Timing settings (in seconds)
MIN_DELAY = 2
MAX_DELAY = 8
TYPING_SPEED = 50  # characters per second