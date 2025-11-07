# AI Telegram Bots Orchestrator - React Frontend

React приложение для управления телеграм ботами через веб-интерфейс.

## Установка

```bash
npm install
```

## Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно по адресу `http://localhost:3000`

## Сборка для продакшена

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Предпросмотр продакшен сборки

```bash
npm run preview
```

## Структура проекта

```
static/
├── public/
│   └── index.html          # HTML шаблон
├── src/
│   ├── App.jsx             # Главный компонент приложения
│   ├── index.jsx           # Точка входа React
│   └── index.css           # Стили приложения
├── package.json            # Зависимости и скрипты
└── vite.config.js          # Конфигурация Vite
```

## API

Приложение использует API из основного проекта. Прокси настроен в `vite.config.js` для перенаправления запросов `/api/*` на `http://localhost:8000`.

