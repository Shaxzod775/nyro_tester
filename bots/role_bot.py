"""
Базовые классы для телеграм ботов с разными ролями
"""

import asyncio
from typing import Dict
from telegram import Bot
from telegram.error import TelegramError
from config import TYPING_SPEED


class RoleBot:
    """Базовый класс для бота с ролью"""

    def __init__(self, token: str, personality: Dict):
        """
        Инициализация бота

        Args:
            token: Telegram Bot API token
            personality: Словарь с информацией о личности бота
        """
        self.token = token
        self.bot = Bot(token=token)
        self.name = personality.get("name", "Bot")
        self.role = personality.get("role", "Unknown")
        self.personality = personality.get("personality", "")

    async def get_me(self):
        """
        Получает информацию о боте

        Returns:
            User object или None в случае ошибки
        """
        try:
            return await self.bot.get_me()
        except TelegramError as e:
            print(f"Ошибка получения информации о боте {self.name}: {e}")
            return None

    async def send_message(self, chat_id: int, text: str):
        """
        Отправляет сообщение в чат

        Args:
            chat_id: ID чата
            text: Текст сообщения

        Returns:
            Message object или None в случае ошибки
        """
        try:
            return await self.bot.send_message(
                chat_id=chat_id,
                text=text
            )
        except TelegramError as e:
            print(f"Ошибка отправки сообщения от {self.name}: {e}")
            return None

    async def send_typing_action(self, chat_id: int):
        """
        Отправляет действие 'печатает...'

        Args:
            chat_id: ID чата
        """
        try:
            await self.bot.send_chat_action(
                chat_id=chat_id,
                action="typing"
            )
        except TelegramError as e:
            print(f"Ошибка отправки typing action от {self.name}: {e}")

    async def send_message_with_typing(self, chat_id: int, text: str, delay: float = 0):
        """
        Отправляет сообщение с имитацией печати

        Args:
            chat_id: ID чата
            text: Текст сообщения
            delay: Задержка перед началом печати (в секундах)

        Returns:
            Message object или None в случае ошибки
        """
        # Ждем перед началом
        if delay > 0:
            await asyncio.sleep(delay)

        # Показываем "печатает..."
        await self.send_typing_action(chat_id)

        # Имитируем время печати на основе длины сообщения
        typing_time = min(len(text) / TYPING_SPEED, 5)  # Максимум 5 секунд
        await asyncio.sleep(typing_time)

        # Отправляем сообщение
        return await self.send_message(chat_id, text)

    def __str__(self):
        return f"{self.name} ({self.role})"


class PMBot(RoleBot):
    """Бот - Project Manager"""

    def __init__(self, token: str, personality: Dict):
        super().__init__(token, personality)


class ClientBot(RoleBot):
    """Бот - Заказчик"""

    def __init__(self, token: str, personality: Dict):
        super().__init__(token, personality)


class DeveloperBot(RoleBot):
    """Бот - Разработчик"""

    def __init__(self, token: str, personality: Dict):
        super().__init__(token, personality)
