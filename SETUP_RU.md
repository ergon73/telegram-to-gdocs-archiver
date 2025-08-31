# 🚀 Настройка Telegram to Google Docs Archiver

## 📋 Пошаговая инструкция

### 1. Получение учетных данных Telegram

1. **Перейдите на [my.telegram.org/apps](https://my.telegram.org/apps)**
2. **Войдите в свой аккаунт Telegram**
3. **Создайте новое приложение:**
   - App title: `Telegram Archiver`
   - Short name: `tg_archiver`
   - Platform: `Desktop`
   - Description: `Archiver for Telegram messages to Google Docs`
4. **Скопируйте:**
   - `api_id` (число)
   - `api_hash` (строка)

### 2. Настройка Google Cloud

1. **Перейдите в [Google Cloud Console](https://console.cloud.google.com/)**
2. **Создайте новый проект:**
   - Нажмите "Select a project" → "New Project"
   - Название: `Telegram Archiver`
   - Нажмите "Create"
3. **Включите Google Docs API:**
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Google Docs API"
   - Нажмите "Enable"
4. **Создайте учетные данные:**
   - Перейдите в "APIs & Services" → "Credentials"
   - Нажмите "Create Credentials" → "OAuth client ID"
   - Application type: `Desktop app`
   - Name: `Telegram Archiver Desktop`
   - Нажмите "Create"
5. **Скачайте файл:**
   - Нажмите "Download JSON"
   - Переименуйте в `credentials.json`
   - Поместите в корень проекта

### 3. Получение ID канала

#### Для публичных каналов:
1. Откройте канал в Telegram
2. Скопируйте username (без @)
3. ID будет: `@username`

#### Для приватных каналов:
1. Перешлите любое сообщение из канала [@userinfobot](https://t.me/userinfobot)
2. Бот покажет ID канала (обычно отрицательное число, например: `-1001234567890`)

### 4. Получение ID Google Doc

1. **Откройте ваш Google Doc**
2. **Скопируйте ID из URL:**
   ```
   https://docs.google.com/document/d/[ЭТО_ИД]/edit
   ```
   Например: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

### 5. Настройка конфигурации

1. **Скопируйте пример конфигурации:**
   ```bash
   cp config/.env.example .env
   ```

2. **Отредактируйте файл `.env`:**
   ```bash
   # Конфигурация Telegram
   TELEGRAM_API_ID=12345678
   TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
   TELEGRAM_CHANNEL_ID=-1001234567890
   TELEGRAM_SESSION_NAME=archiver_bot

   # Конфигурация Google  
   GOOGLE_DOC_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
   GOOGLE_CREDENTIALS_PATH=credentials.json

   # Конфигурация обработки
   BATCH_SIZE=5
   CHECK_INTERVAL=30
   MAX_RETRIES=3
   ```

### 6. Первый запуск

1. **Проверьте соединения:**
   ```bash
   python -m src.main --test
   ```

2. **При первом запуске:**
   - Откроется браузер для аутентификации Google
   - Введите номер телефона Telegram
   - Введите код подтверждения

3. **Запустите архиватор:**
   ```bash
   python -m src.main
   ```

## 🔧 Устранение неполадок

### Ошибка аутентификации Google
```bash
# Удалите токен и переаутентифицируйтесь
rm data/state/token.pickle
python -m src.main
```

### Ошибка сессии Telegram
```bash
# Удалите файл сессии и переаутентифицируйтесь
rm archiver_bot.session
python -m src.main
```

### Проблемы с правами доступа
- **Telegram**: Убедитесь, что у вас есть доступ к каналу
- **Google Docs**: Убедитесь, что у вас есть права на редактирование документа

### Ошибка "Channel not found"
- Проверьте правильность ID канала
- Убедитесь, что вы являетесь участником канала

### Ошибка "Document not found"
- Проверьте правильность ID Google Doc
- Убедитесь, что документ существует и доступен

## 📊 Мониторинг работы

### Просмотр логов
```bash
tail -f data/logs/archiver.log
```

### Проверка статистики
```bash
python -m src.main --test
```

### Режим отладки
```bash
python -m src.main --debug
```

## 📝 Интеграция с NotebookLM

1. **Запустите архиватор**
2. **Перейдите в [NotebookLM](https://notebooklm.google.com/)**
3. **Откройте ваш Google Doc**
4. **Нажмите "Sync"**
5. **Задавайте вопросы ИИ о контенте**

## 🎯 Что архивируется

- ✅ **Текст сообщений** из пересланных сообщений
- ✅ **Ссылки** (очищенные и кликабельные)
- ✅ **Метаданные пересылки** (источник, дата)
- ✅ **Подписи к медиа** (фото, документы)
- ✅ **Временные метки**
- ✅ **Форматирование** (цвета, жирный, курсив)

## 📞 Поддержка

Если у вас возникли проблемы:

1. **Проверьте логи** в `data/logs/archiver.log`
2. **Поищите решение** в разделе устранения неполадок
3. **Откройте проблему** на GitHub с подробным описанием

---

**Удачной настройки! 🚀**
