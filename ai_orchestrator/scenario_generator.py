import openai
import json
import random
from typing import List, Dict
from config import OPENAI_API_KEY, BOT_PERSONALITIES, MIN_MESSAGES, MAX_MESSAGES, MIN_DELAY, MAX_DELAY

openai.api_key = OPENAI_API_KEY


class ScenarioGenerator:
    """Генератор сценариев диалогов для ботов"""
    
    def __init__(self):
        self.personalities = BOT_PERSONALITIES
    
    def generate_scenario(self, user_prompt: str, num_messages: int = None) -> List[Dict]:
        """
        Генерирует сценарий диалога на основе промпта пользователя
        
        Args:
            user_prompt: Описание сценария от пользователя
            num_messages: Количество сообщений (если не указано, используется случайное)
        
        Returns:
            List[Dict]: Список сообщений с форматом:
                [
                    {
                        "agent": "pm",
                        "text": "Текст сообщения",
                        "delay": 5
                    },
                    ...
                ]
        """
        if num_messages is None:
            num_messages = random.randint(MIN_MESSAGES, MAX_MESSAGES)
        
        system_prompt = self._build_system_prompt(num_messages)
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=4000
            )
            
            scenario_text = response.choices[0].message.content
            scenario = self._parse_scenario(scenario_text, num_messages)
            
            return scenario
            
        except Exception as e:
            print(f"Ошибка при генерации сценария: {e}")
            return self._generate_fallback_scenario()
    
    def _build_system_prompt(self, num_messages: int) -> str:
        """Создает системный промпт для OpenAI"""
        
        pm_info = self.personalities["pm"]
        client_info = self.personalities["client"]
        dev_info = self.personalities["dev"]
        
        return f"""Ты создаешь реалистичный сценарий рабочего диалога для трех персонажей в Telegram группе.

ПЕРСОНАЖИ:
1. {pm_info['name']} - {pm_info['role']}
{pm_info['personality']}

2. {client_info['name']} - {client_info['role']}
{client_info['personality']}

3. {dev_info['name']} - {dev_info['role']}
{dev_info['personality']}

ЗАДАЧА:
Создай реалистичный рабочий диалог на {num_messages} сообщений. Диалог должен включать:
- Приветствие и знакомство
- Обсуждение задачи/проекта
- Уточняющие вопросы
- Распределение задач
- Промежуточные обновления
- Решение возникших вопросов
- Завершение проекта

ПРАВИЛА:
- Диалог должен быть естественным и живым
- Используй короткие и средние сообщения (как в реальном чате)
- Добавляй эмодзи где уместно (но не слишком много)
- Персонажи должны соответствовать своим ролям
- Сообщения должны логично следовать друг за другом
- Пиши на русском языке

ФОРМАТ ОТВЕТА:
Верни ТОЛЬКО JSON массив в формате:
[
    {{"agent": "client", "text": "Привет всем! 👋"}},
    {{"agent": "pm", "text": "Здравствуйте! Рад знакомству 😊"}},
    {{"agent": "dev", "text": "Привет! Готов приступить 💻"}}
]

Где agent может быть: "pm", "client", или "dev"

НЕ добавляй никакого текста кроме JSON массива."""
    
    def _parse_scenario(self, scenario_text: str, expected_count: int) -> List[Dict]:
        """Парсит ответ от OpenAI и добавляет задержки"""
        
        try:
            # Убираем markdown code blocks если есть
            scenario_text = scenario_text.strip()
            if scenario_text.startswith("```"):
                scenario_text = scenario_text.split("```")[1]
                if scenario_text.startswith("json"):
                    scenario_text = scenario_text[4:]
            
            messages = json.loads(scenario_text)
            
            # Добавляем случайные задержки
            for message in messages:
                text_length = len(message["text"])
                base_delay = random.uniform(MIN_DELAY, MAX_DELAY)
                
                # Более длинные сообщения = дольше "печатают"
                if text_length > 100:
                    base_delay += random.uniform(2, 4)
                elif text_length > 50:
                    base_delay += random.uniform(1, 2)
                
                message["delay"] = round(base_delay, 1)
            
            return messages
            
        except Exception as e:
            print(f"Ошибка парсинга сценария: {e}")
            print(f"Текст ответа: {scenario_text}")
            return self._generate_fallback_scenario()
    
    def _generate_fallback_scenario(self) -> List[Dict]:
        """Резервный сценарий на случай ошибки API"""
        
        return [
            {"agent": "client", "text": "Привет всем! 👋 Нужна помощь с небольшим проектом.", "delay": 3},
            {"agent": "pm", "text": "Здравствуйте! Рад знакомству 😊 Расскажите подробнее о проекте.", "delay": 4},
            {"agent": "dev", "text": "Привет! Готов приступить 💻", "delay": 2},
            {"agent": "client", "text": "Нужно сделать простой веб-сайт для нашей компании. Главная страница, контакты, портфолио.", "delay": 5},
            {"agent": "pm", "text": "Понятно! У вас есть дизайн или примеры сайтов, которые нравятся?", "delay": 3},
            {"agent": "client", "text": "Да, скину примеры. Хотелось бы в современном стиле, минималистично.", "delay": 4},
            {"agent": "dev", "text": "Какие технологии предпочитаете? Есть ли требования по хостингу?", "delay": 5},
            {"agent": "client", "text": "Технологии на ваше усмотрение. Хостинг у нас уже есть.", "delay": 3},
            {"agent": "pm", "text": "Отлично! Дмитрий, можешь оценить сроки? 📋", "delay": 4},
            {"agent": "dev", "text": "Думаю 2 недели будет достаточно. Сделаю на React + Tailwind.", "delay": 5},
            {"agent": "pm", "text": "Супер! Мария, вас устраивают сроки?", "delay": 2},
            {"agent": "client", "text": "Да, отлично! Когда можно увидеть первые результаты?", "delay": 3},
            {"agent": "dev", "text": "Через 3-4 дня покажу прототип главной страницы ✨", "delay": 4},
            {"agent": "pm", "text": "Отлично, я буду координировать процесс. Начинаем! 🚀", "delay": 3},
            {"agent": "client", "text": "Спасибо! Жду результатов 😊", "delay": 2}
        ]


if __name__ == "__main__":
    # Тестирование генератора
    generator = ScenarioGenerator()
    scenario = generator.generate_scenario("Создай диалог про разработку мобильного приложения", 20)
    
    print("Сгенерированный сценарий:")
    print(json.dumps(scenario, ensure_ascii=False, indent=2))