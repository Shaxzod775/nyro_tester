import { useState, useEffect, useRef } from 'react';

// const API_URL = 'https://nyro-bot-tester.ailab.uz';
const API_URL = 'http://localhost:8000';

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
  const [batchSize, setBatchSize] = useState('5');
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
  const [executionStatus, setExecutionStatus] = useState({
    is_running: false,
    is_paused: false,
    messages_sent: 0,
    total_messages: 0,
    current_batch: 0,
    total_batches: 0
  });
  const statusIntervalRef = useRef(null);
  const autoStatusIntervalRef = useRef(null);
  const executionIntervalRef = useRef(null);

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

  const loadExecutionStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/execution-status`);
      const data = await response.json();
      setExecutionStatus(data);
      setIsRunning(data.is_running);

      // Если выполнение завершено, останавливаем polling
      if (!data.is_running && executionIntervalRef.current) {
        clearInterval(executionIntervalRef.current);
        executionIntervalRef.current = null;
      }
    } catch (error) {
      console.error('Ошибка загрузки статуса выполнения:', error);
    }
  };

  const handleResume = async () => {
    try {
      const response = await fetch(`${API_URL}/api/resume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();

      if (response.ok) {
        showAlert(data.message, 'success');
        await loadExecutionStatus();
      } else {
        showAlert(`Ошибка: ${data.detail}`, 'error');
      }
    } catch (error) {
      showAlert('Ошибка запроса: ' + error.message, 'error');
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
      chat_id: chatId ? parseInt(chatId) : null,
      batch_size: batchSize ? parseInt(batchSize) : 5
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

        // Запускаем polling для execution status
        if (executionIntervalRef.current) {
          clearInterval(executionIntervalRef.current);
        }
        executionIntervalRef.current = setInterval(async () => {
          await loadExecutionStatus();
        }, 1000);
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
    loadExecutionStatus();

    // Автообновление статуса каждые 10 секунд
    autoStatusIntervalRef.current = setInterval(loadStatus, 10000);

    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
      if (autoStatusIntervalRef.current) {
        clearInterval(autoStatusIntervalRef.current);
      }
      if (executionIntervalRef.current) {
        clearInterval(executionIntervalRef.current);
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

            <div className="form-group">
              <label htmlFor="batchSize">
                Размер батча (количество сообщений перед паузой):
              </label>
              <input
                type="number"
                id="batchSize"
                value={batchSize}
                onChange={(e) => setBatchSize(e.target.value)}
                placeholder="По умолчанию: 5"
                min="1"
                max="50"
              />
              <small style={{ color: '#999', marginTop: '5px', display: 'block' }}>
                После отправки указанного количества сообщений будет пауза
              </small>
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

      {/* Статус выполнения */}
      {isRunning && (
        <div className="card">
          <h2>Статус выполнения</h2>
          <div style={{ marginBottom: '20px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '10px',
              fontSize: '14px',
              color: '#666'
            }}>
              <span>
                Отправлено: {executionStatus.messages_sent} / {executionStatus.total_messages}
              </span>
              <span>
                Батч: {executionStatus.current_batch} / {executionStatus.total_batches}
              </span>
            </div>

            {/* Прогресс бар */}
            <div style={{
              width: '100%',
              height: '30px',
              backgroundColor: '#e0e0e0',
              borderRadius: '15px',
              overflow: 'hidden',
              position: 'relative'
            }}>
              <div style={{
                width: `${executionStatus.total_messages > 0
                  ? (executionStatus.messages_sent / executionStatus.total_messages * 100)
                  : 0}%`,
                height: '100%',
                backgroundColor: executionStatus.is_paused ? '#ffa500' : '#667eea',
                transition: 'width 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '14px'
              }}>
                {executionStatus.total_messages > 0
                  ? Math.round((executionStatus.messages_sent / executionStatus.total_messages) * 100)
                  : 0}%
              </div>
            </div>

            {/* Статус паузы */}
            {executionStatus.is_paused && (
              <div style={{
                marginTop: '20px',
                padding: '15px',
                backgroundColor: '#fff3cd',
                border: '2px solid #ffa500',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{
                  fontSize: '18px',
                  fontWeight: 'bold',
                  color: '#856404',
                  marginBottom: '10px'
                }}>
                  ⏸️ ПАУЗА
                </div>
                <div style={{
                  fontSize: '14px',
                  color: '#856404',
                  marginBottom: '15px'
                }}>
                  Отправлено {executionStatus.messages_sent} из {executionStatus.total_messages} сообщений
                  <br />
                  Батч {executionStatus.current_batch} из {executionStatus.total_batches} завершен
                </div>
                <button
                  className="btn"
                  onClick={handleResume}
                  style={{
                    backgroundColor: '#28a745',
                    fontSize: '16px',
                    padding: '12px 30px'
                  }}
                >
                  ▶️ Продолжить
                </button>
              </div>
            )}

            {/* Статус выполнения */}
            {!executionStatus.is_paused && executionStatus.is_running && (
              <div style={{
                marginTop: '15px',
                textAlign: 'center',
                color: '#667eea',
                fontWeight: 'bold'
              }}>
                ⚙️ Отправка сообщений...
              </div>
            )}
          </div>
        </div>
      )}

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

