import { useState, useEffect, useRef } from 'react';

const API_URL = 'https://nyro-bot-tester.ailab.uz';

const ROLE_NAMES = {
  pm: 'PM Bot',
  dev: 'Developer Bot',
  client: 'Client Bot'
};

const SCENARIO_ROLE_NAMES = {
  pm: 'Алексей (PM)',
  dev: 'Дмитрий (Developer)',
  client: 'Мария (Client)'
};

const EXAMPLE_PROMPTS = [
  'Создай диалог про разработку мобильного приложения для фитнеса',
  'Сделай обсуждение веб-сайта для ресторана с онлайн-заказами',
  'Диалог про создание интернет-магазина одежды',
  'Обсуждение разработки CRM системы для малого бизнеса',
  'Создай диалог про разработку бота для автоматизации продаж'
];

function App() {
  const [prompt, setPrompt] = useState('');
  const [numMessages, setNumMessages] = useState('');
  const [chatId, setChatId] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [alert, setAlert] = useState({ message: '', type: 'info', show: false });
  const [botsStatus, setBotsStatus] = useState({
    pm: { status: 'loading', username: 'Загрузка...' },
    dev: { status: 'loading', username: 'Загрузка...' },
    client: { status: 'loading', username: 'Загрузка...' }
  });
  const [scenario, setScenario] = useState([]);
  const [scenarioCount, setScenarioCount] = useState(0);
  const [configChatId, setConfigChatId] = useState(null);
  const statusIntervalRef = useRef(null);
  const autoStatusIntervalRef = useRef(null);

  const showAlert = (message, type = 'info') => {
    setAlert({ message, type, show: true });
    setTimeout(() => {
      setAlert({ message: '', type: 'info', show: false });
    }, 5000);
  };

  const loadStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/status`);
      const data = await response.json();

      const newBotsStatus = {};
      for (const [role, bot] of Object.entries(data.bots)) {
        newBotsStatus[role] = {
          status: bot.status,
          username: bot.username
        };
      }
      setBotsStatus(newBotsStatus);
      setIsRunning(data.is_running);
    } catch (error) {
      showAlert('Ошибка загрузки статуса: ' + error.message, 'error');
    }
  };

  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/api/config`);
      const data = await response.json();

      if (data.target_chat_id) {
        setConfigChatId(data.target_chat_id);
      }
    } catch (error) {
      console.error('Ошибка загрузки конфигурации:', error);
    }
  };

  const loadScenario = async () => {
    try {
      const response = await fetch(`${API_URL}/api/scenario`);
      const data = await response.json();

      if (data.scenario && data.scenario.length > 0) {
        setScenario(data.scenario);
        setScenarioCount(data.count);
      } else {
        setScenario([]);
        setScenarioCount(0);
      }
    } catch (error) {
      console.error('Ошибка загрузки сценария:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const promptValue = prompt.trim();
    if (!promptValue) {
      showAlert('Введите описание сценария!', 'error');
      return;
    }

    const payload = {
      prompt: promptValue,
      num_messages: numMessages ? parseInt(numMessages) : null,
      chat_id: chatId ? parseInt(chatId) : null
    };

    setIsRunning(true);
    showAlert('Генерация сценария...', 'info');

    try {
      const response = await fetch(`${API_URL}/api/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        showAlert(`Успешно! ${data.message}`, 'success');
        await loadScenario();

        // Обновляем статус каждые 2 секунды пока выполняется
        if (statusIntervalRef.current) {
          clearInterval(statusIntervalRef.current);
        }
        statusIntervalRef.current = setInterval(async () => {
          await loadStatus();
          const statusResponse = await fetch(`${API_URL}/api/status`);
          const statusData = await statusResponse.json();
          if (!statusData.is_running) {
            clearInterval(statusIntervalRef.current);
            statusIntervalRef.current = null;
            setIsRunning(false);
          }
        }, 2000);
      } else {
        showAlert(`Ошибка: ${data.detail}`, 'error');
        setIsRunning(false);
      }
    } catch (error) {
      showAlert('Ошибка запроса: ' + error.message, 'error');
      setIsRunning(false);
    }
  };

  const handleExampleClick = (examplePrompt) => {
    setPrompt(examplePrompt);
  };

  useEffect(() => {
    loadStatus();
    loadConfig();
    loadScenario();

    // Автообновление статуса каждые 10 секунд
    autoStatusIntervalRef.current = setInterval(loadStatus, 10000);

    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
      if (autoStatusIntervalRef.current) {
        clearInterval(autoStatusIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="container">
      <div className="header">
        <h1>AI Telegram Bots Orchestrator</h1>
        <p>Управление телеграм ботами через веб-интерфейс</p>
      </div>

      {alert.show && (
        <div className={`alert alert-${alert.type} show`}>
          {alert.message}
        </div>
      )}

      <div className="main-content">
        {/* Левая колонка: Форма */}
        <div className="card">
          <h2>Создать диалог</h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="prompt">Описание сценария:</label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Например: Создай диалог про разработку мобильного приложения для фитнеса"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="numMessages">Количество сообщений:</label>
              <input
                type="number"
                id="numMessages"
                value={numMessages}
                onChange={(e) => setNumMessages(e.target.value)}
                placeholder="Оставьте пустым для авто (20-35)"
                min="10"
                max="50"
              />
            </div>

            <div className="form-group">
              <label htmlFor="chatId">
                Chat ID{' '}
                <span
                  className="info-badge"
                  style={{
                    background: configChatId ? '#28a745' : '#667eea'
                  }}
                >
                  {configChatId || 'не настроен'}
                </span>
              </label>
              <input
                type="text"
                id="chatId"
                value={chatId}
                onChange={(e) => setChatId(e.target.value)}
                placeholder={
                  configChatId
                    ? `Использовать: ${configChatId}`
                    : 'Оставьте пустым для использования из .env'
                }
              />
            </div>

            <button
              type="submit"
              className="btn"
              disabled={isRunning}
            >
              {isRunning ? 'Выполняется...' : 'Запустить полный цикл'}
            </button>
          </form>

          <div className="examples">
            <h4>Примеры промптов (кликните для выбора):</h4>
            <ul>
              {EXAMPLE_PROMPTS.map((example, index) => (
                <li
                  key={index}
                  onClick={() => handleExampleClick(example)}
                >
                  {example}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Правая колонка: Статус */}
        <div className="card">
          <h2>Статус системы</h2>

          <div className="status-grid">
            {Object.entries(botsStatus).map(([role, bot]) => (
              <div
                key={role}
                className={`bot-status ${
                  bot.status === 'online' ? 'online' : 'offline'
                }`}
              >
                <h3>{ROLE_NAMES[role]}</h3>
                <p>{bot.username}</p>
              </div>
            ))}
          </div>

          <button
            className="btn btn-secondary"
            onClick={loadStatus}
          >
            Обновить статус
          </button>
        </div>
      </div>

      {/* Сценарий */}
      <div className="card">
        <h2>
          Текущий сценарий{' '}
          <span className="info-badge">
            {scenarioCount} сообщений
          </span>
        </h2>
        <div className="scenario-list">
          {scenario.length > 0 ? (
            scenario.map((msg, index) => (
              <div key={index} className="scenario-item">
                <div className="agent">
                  [{index + 1}] {SCENARIO_ROLE_NAMES[msg.agent]}
                </div>
                <div className="text">{msg.text}</div>
              </div>
            ))
          ) : (
            <p style={{ textAlign: 'center', color: '#999' }}>
              Сценарий не сгенерирован
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

