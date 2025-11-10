#!/usr/bin/env python3
"""
FastAPI Backend для управления AI Telegram Bots
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
from pathlib import Path

from coordinator import Coordinator
from config import TARGET_CHAT_ID

# Создаем приложение
app = FastAPI(
    title="AI Telegram Bots Orchestrator",
    description="API для управления телеграм ботами с AI",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный координатор
coordinator = Coordinator()
is_running = False

# Состояние выполнения с паузами
execution_state = {
    "is_paused": False,
    "messages_sent": 0,
    "total_messages": 0,
    "current_batch": 0,
    "total_batches": 0,
    "resume_event": None
}


# Модели данных
class RunRequest(BaseModel):
    prompt: str
    num_messages: Optional[int] = None
    chat_id: Optional[int] = None
    batch_size: Optional[int] = 5


class GenerateRequest(BaseModel):
    prompt: str
    num_messages: Optional[int] = None


class ExecuteRequest(BaseModel):
    chat_id: Optional[int] = None
    batch_size: Optional[int] = 5


class StatusResponse(BaseModel):
    bots: Dict[str, Dict[str, str]]
    is_running: bool
    has_scenario: bool


class ScenarioResponse(BaseModel):
    scenario: Optional[List[Dict]] = None
    count: int


class ExecutionStatusResponse(BaseModel):
    is_running: bool
    is_paused: bool
    messages_sent: int
    total_messages: int
    current_batch: int
    total_batches: int


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница - отдаем HTML интерфейс"""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return """
    <html>
        <body>
            <h1>AI Telegram Bots Orchestrator</h1>
            <p>Frontend not found. Please create static/index.html</p>
            <p>API Documentation: <a href="/docs">/docs</a></p>
        </body>
    </html>
    """


@app.get("/api/health")
async def health():
    """Проверка здоровья API"""
    return {"status": "ok", "message": "API is running"}


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Получить статус ботов"""
    global is_running

    bots_status = {}
    for role, bot in coordinator.bots.items():
        info = await bot.get_me()
        if info:
            bots_status[role] = {
                "name": bot.name,
                "username": f"@{info.username}",
                "id": str(info.id),
                "status": "online"
            }
        else:
            bots_status[role] = {
                "name": bot.name,
                "username": "Unknown",
                "id": "Unknown",
                "status": "offline"
            }

    return StatusResponse(
        bots=bots_status,
        is_running=is_running,
        has_scenario=coordinator.current_scenario is not None
    )


@app.get("/api/scenario", response_model=ScenarioResponse)
async def get_scenario():
    """Получить текущий сценарий"""
    if coordinator.current_scenario is None:
        return ScenarioResponse(scenario=None, count=0)

    return ScenarioResponse(
        scenario=coordinator.current_scenario,
        count=len(coordinator.current_scenario)
    )


@app.post("/api/generate")
async def generate_scenario(request: GenerateRequest):
    """Генерировать новый сценарий"""
    try:
        scenario = coordinator.generate_scenario(
            user_prompt=request.prompt,
            num_messages=request.num_messages
        )

        return {
            "success": True,
            "message": f"Сценарий сгенерирован: {len(scenario)} сообщений",
            "scenario": scenario,
            "count": len(scenario)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute")
async def execute_scenario(request: ExecuteRequest):
    """Выполнить текущий сценарий"""
    global is_running

    if coordinator.current_scenario is None:
        raise HTTPException(
            status_code=400,
            detail="Нет сценария для выполнения. Сначала сгенерируйте сценарий."
        )

    if is_running:
        raise HTTPException(
            status_code=400,
            detail="Сценарий уже выполняется!"
        )

    chat_id = request.chat_id or TARGET_CHAT_ID

    if not chat_id or chat_id == "your_chat_id_here":
        raise HTTPException(
            status_code=400,
            detail="Chat ID не установлен. Добавьте TARGET_CHAT_ID в .env"
        )

    # Запускаем в фоновом режиме
    asyncio.create_task(run_scenario_background(chat_id, request.batch_size))

    return {
        "success": True,
        "message": "Выполнение сценария начато",
        "chat_id": chat_id,
        "messages_count": len(coordinator.current_scenario),
        "batch_size": request.batch_size
    }


@app.post("/api/run")
async def run_full_cycle(request: RunRequest):
    """Полный цикл: генерация + выполнение"""
    global is_running

    if is_running:
        raise HTTPException(
            status_code=400,
            detail="Сценарий уже выполняется!"
        )

    chat_id = request.chat_id or TARGET_CHAT_ID

    if not chat_id or chat_id == "your_chat_id_here":
        raise HTTPException(
            status_code=400,
            detail="Chat ID не установлен. Добавьте TARGET_CHAT_ID в .env"
        )

    try:
        # Генерируем сценарий
        scenario = coordinator.generate_scenario(
            user_prompt=request.prompt,
            num_messages=request.num_messages
        )

        # Запускаем в фоновом режиме
        asyncio.create_task(run_scenario_background(chat_id, request.batch_size))

        return {
            "success": True,
            "message": "Сценарий сгенерирован и запущен",
            "chat_id": chat_id,
            "messages_count": len(scenario),
            "batch_size": request.batch_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def run_scenario_background(chat_id: int, batch_size: int = 5):
    """Фоновое выполнение сценария с батчами и паузами"""
    global is_running, execution_state
    is_running = True

    try:
        await coordinator.execute_scenario_with_batches(chat_id, batch_size, execution_state)
    except Exception as e:
        print(f"Ошибка выполнения сценария: {e}")
    finally:
        is_running = False
        execution_state["is_paused"] = False
        execution_state["messages_sent"] = 0
        execution_state["total_messages"] = 0
        execution_state["current_batch"] = 0
        execution_state["total_batches"] = 0
        execution_state["resume_event"] = None


@app.get("/api/execution-status", response_model=ExecutionStatusResponse)
async def get_execution_status():
    """Получить статус выполнения сценария"""
    global execution_state, is_running

    return ExecutionStatusResponse(
        is_running=is_running,
        is_paused=execution_state["is_paused"],
        messages_sent=execution_state["messages_sent"],
        total_messages=execution_state["total_messages"],
        current_batch=execution_state["current_batch"],
        total_batches=execution_state["total_batches"]
    )


@app.post("/api/resume")
async def resume_execution():
    """Продолжить выполнение после паузы"""
    global execution_state

    if not execution_state["is_paused"]:
        raise HTTPException(
            status_code=400,
            detail="Выполнение не приостановлено"
        )

    if execution_state["resume_event"]:
        execution_state["resume_event"].set()
        return {
            "success": True,
            "message": "Выполнение продолжено"
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Нет активного события для продолжения"
        )


@app.get("/api/config")
async def get_config():
    """Получить текущую конфигурацию"""
    from config import BOT_PERSONALITIES, MODEL_NAME, MIN_MESSAGES, MAX_MESSAGES

    return {
        "model": MODEL_NAME,
        "min_messages": MIN_MESSAGES,
        "max_messages": MAX_MESSAGES,
        "target_chat_id": TARGET_CHAT_ID if TARGET_CHAT_ID != "your_chat_id_here" else None,
        "bots": {
            role: {
                "name": info["name"],
                "role": info["role"]
            }
            for role, info in BOT_PERSONALITIES.items()
        }
    }


# Монтируем статические файлы
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


if __name__ == "__main__":
    import uvicorn

    print("🚀 Запуск API сервера...")
    print("📱 Веб-интерфейс: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
