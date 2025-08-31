# 🚀 Быстрый старт - Telegram to Google Docs Archiver

## 📋 Что это такое?

Это приложение автоматически архивирует сообщения из каналов Telegram в Google Docs для последующего анализа с помощью NotebookLM.

## ⚡ Установка за 5 минут

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/ergon73/telegram-to-gdocs-archiver.git
cd telegram-to-gdocs-archiver
```

### 2. Установите зависимости
```bash
pip install -r requirements.txt
```

### 3. Настройте учетные данные

#### Telegram API
1. Перейдите на [my.telegram.org/apps](https://my.telegram.org/apps)
2. Создайте приложение
3. Скопируйте `api_id` и `api_hash`

#### Google Cloud
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект
3. Включите Google Docs API
4. Создайте OAuth 2.0 учетные данные (Desktop app)
5. Скачайте `credentials.json`

### 4. Настройте конфигурацию
```bash
cp config/.env.example .env
```

Отредактируйте `.env`:
```bash
TELEGRAM_API_ID=ваш_api_id
TELEGRAM_API_HASH=ваш_api_hash
TELEGRAM_CHANNEL_ID=id_вашего_канала
GOOGLE_DOC_ID=id_вашего_google_doc
GOOGLE_CREDENTIALS_PATH=credentials.json
```

### 5. Запустите
```bash
python -m src.main
```

## 🔧 Настройка канала

### Получение ID канала
1. Перешлите любое сообщение из канала [@userinfobot](https://t.me/userinfobot)
2. Бот покажет ID канала (обычно отрицательное число)

### Получение ID Google Doc
1. Откройте ваш Google Doc
2. Скопируйте ID из URL: `https://docs.google.com/document/d/[ID]/edit`

## 📝 Использование с NotebookLM

1. Запустите архиватор
2. Перейдите в [NotebookLM](https://notebooklm.google.com/)
3. Откройте ваш Google Doc
4. Нажмите "Sync"
5. Задавайте вопросы ИИ о контенте

## 🛠️ Команды

```bash
# Проверка соединений
python -m src.main --test

# Обычный запуск
python -m src.main

# Режим отладки
python -m src.main --debug
```

## 🔧 Устранение неполадок

### Ошибка аутентификации
```bash
rm data/state/token.pickle
python -m src.main
```

### Ошибка сессии Telegram
```bash
rm archiver_bot.session
python -m src.main
```

### Проблемы с правами доступа
- Убедитесь, что у вас есть доступ к каналу
- Проверьте права на Google Doc

## 📊 Мониторинг

### Логи
```bash
tail -f data/logs/archiver.log
```

### Статистика
```bash
python -m src.main --test
```

## 🎯 Что архивируется

- ✅ Текст сообщений
- ✅ Ссылки (очищенные)
- ✅ Метаданные пересылок
- ✅ Подписи к медиа
- ✅ Временные метки
- ✅ Форматирование (цвета, жирный)

## 📞 Поддержка

- 📖 [Полная документация](README_RU.md)
- 🐛 [Проблемы на GitHub](https://github.com/ergon73/telegram-to-gdocs-archiver/issues)
- 💬 [Обсуждения](https://github.com/ergon73/telegram-to-gdocs-archiver/discussions)

---

**Готово! Ваш архиватор работает! 🚀**
