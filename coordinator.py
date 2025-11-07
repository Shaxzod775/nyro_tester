import asyncio
from typing import List, Dict
from bots.role_bot import PMBot, ClientBot, DeveloperBot
from ai_orchestrator.scenario_generator import ScenarioGenerator
from config import (
    PM_BOT_TOKEN, CLIENT_BOT_TOKEN, DEV_BOT_TOKEN,
    TARGET_CHAT_ID, BOT_PERSONALITIES
)


class Coordinator:
    """
    Координатор - управляет всеми ботами и выполнением сценариев
    """
    
    def __init__(self):
        """Инициализация координатора и всех ботов"""
        
        print("🚀 Инициализация координатора...")
        
        # Создаем ботов
        self.bots = {
            "pm": PMBot(PM_BOT_TOKEN, BOT_PERSONALITIES["pm"]),
            "client": ClientBot(CLIENT_BOT_TOKEN, BOT_PERSONALITIES["client"]),
            "dev": DeveloperBot(DEV_BOT_TOKEN, BOT_PERSONALITIES["dev"])
        }
        
        # Создаем генератор сценариев
        self.scenario_generator = ScenarioGenerator()
        
        # Текущий сценарий
        self.current_scenario = None
        self.is_running = False
        
        print("✅ Координатор инициализирован")
    
    async def check_bots(self) -> bool:
        """
        Проверяет, что все боты доступны
        
        Returns:
            bool: True если все боты работают
        """
        print("\n🔍 Проверка ботов...")
        
        all_ok = True
        for role, bot in self.bots.items():
            bot_info = await bot.get_me()
            if bot_info:
                print(f"  ✅ {bot.name} (@{bot_info.username}) - OK")
            else:
                print(f"  ❌ {bot.name} - ОШИБКА")
                all_ok = False
        
        return all_ok
    
    def generate_scenario(self, user_prompt: str, num_messages: int = None) -> List[Dict]:
        """
        Генерирует новый сценарий
        
        Args:
            user_prompt: Описание сценария от пользователя
            num_messages: Количество сообщений (опционально)
        
        Returns:
            List[Dict]: Сгенерированный сценарий
        """
        print(f"\n🎬 Генерация сценария: '{user_prompt}'")
        
        if num_messages:
            print(f"   Количество сообщений: {num_messages}")
        
        self.current_scenario = self.scenario_generator.generate_scenario(
            user_prompt, 
            num_messages
        )
        
        print(f"✅ Сценарий сгенерирован: {len(self.current_scenario)} сообщений")
        
        return self.current_scenario
    
    async def execute_scenario(self, chat_id: int = None, scenario: List[Dict] = None):
        """
        Выполняет сценарий - боты отправляют сообщения в чат
        
        Args:
            chat_id: ID чата (если не указан, используется TARGET_CHAT_ID из config)
            scenario: Сценарий для выполнения (если не указан, используется current_scenario)
        """
        
        if chat_id is None:
            chat_id = TARGET_CHAT_ID
        
        if scenario is None:
            scenario = self.current_scenario
        
        if scenario is None:
            print("❌ Нет сценария для выполнения!")
            return
        
        if self.is_running:
            print("⚠️  Сценарий уже выполняется!")
            return
        
        self.is_running = True
        
        print(f"\n▶️  Начало выполнения сценария в чате {chat_id}")
        print(f"   Всего сообщений: {len(scenario)}\n")
        
        try:
            for i, message in enumerate(scenario, 1):
                agent_role = message.get("agent")
                text = message.get("text")
                delay = message.get("delay", 0)
                
                if agent_role not in self.bots:
                    print(f"⚠️  Неизвестная роль: {agent_role}, пропускаем сообщение")
                    continue
                
                bot = self.bots[agent_role]
                
                print(f"[{i}/{len(scenario)}] {bot.name} отправляет сообщение через {delay}с...")
                
                await bot.send_message_with_typing(
                    chat_id=chat_id,
                    text=text,
                    delay=delay
                )
                
                # Небольшая дополнительная пауза для естественности
                await asyncio.sleep(0.5)
            
            print(f"\n✅ Сценарий выполнен! Отправлено {len(scenario)} сообщений")
            
        except Exception as e:
            print(f"\n❌ Ошибка при выполнении сценария: {e}")
        
        finally:
            self.is_running = False
    
    async def run_full_cycle(self, user_prompt: str, chat_id: int = None, num_messages: int = None):
        """
        Полный цикл: генерация + выполнение сценария
        
        Args:
            user_prompt: Описание сценария
            chat_id: ID чата (опционально)
            num_messages: Количество сообщений (опционально)
        """
        
        # Проверяем ботов
        if not await self.check_bots():
            print("❌ Не все боты доступны! Проверьте токены.")
            return
        
        # Генерируем сценарий
        scenario = self.generate_scenario(user_prompt, num_messages)
        
        # Ждем немного перед началом
        print("\n⏳ Начинаем через 3 секунды...")
        await asyncio.sleep(3)
        
        # Выполняем сценарий
        await self.execute_scenario(chat_id, scenario)
    
    def print_scenario(self, scenario: List[Dict] = None):
        """Красиво выводит сценарий в консоль"""
        
        if scenario is None:
            scenario = self.current_scenario
        
        if not scenario:
            print("Нет сценария для отображения")
            return
        
        print("\n" + "="*60)
        print("СЦЕНАРИЙ ДИАЛОГА")
        print("="*60 + "\n")
        
        for i, message in enumerate(scenario, 1):
            agent = message.get("agent")
            text = message.get("text")
            delay = message.get("delay", 0)
            
            bot_name = self.bots[agent].name if agent in self.bots else agent
            
            print(f"[{i}] {bot_name} (через {delay}с):")
            print(f"    {text}\n")
        
        print("="*60 + "\n")


async def main():
    """Пример использования координатора"""
    
    coordinator = Coordinator()
    
    # Пример 1: Полный цикл
    await coordinator.run_full_cycle(
        user_prompt="Создай диалог про разработку веб-сайта для ресторана",
        num_messages=25
    )
    
    # Пример 2: Генерация и просмотр сценария без выполнения
    # scenario = coordinator.generate_scenario("Диалог про мобильное приложение", 15)
    # coordinator.print_scenario(scenario)
    
    # Пример 3: Выполнение ранее сгенерированного сценария
    # await coordinator.execute_scenario()


if __name__ == "__main__":
    asyncio.run(main())