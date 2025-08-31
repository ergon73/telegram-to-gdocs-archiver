# Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### 1. Setup Environment
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Go to project directory
cd telegram-to-gdocs-archiver

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
```bash
# Copy and edit environment file
copy config\env.example .env
# Edit .env with your real credentials
```

### 3. Test Everything
```bash
python -m src.main --test
# Follow Google OAuth instructions in browser
```

### 4. Start Archiving
```bash
python -m src.main
```

## 📋 What You Need

- **Telegram API**: Get from https://my.telegram.org/apps
- **Google Cloud**: Create project and enable Docs API
- **Google Doc ID**: From your Google Doc URL
- **Channel ID**: Forward message to @userinfobot

## 🔄 NotebookLM Workflow

1. **Archive messages** → Google Docs (automatic)
2. **Open NotebookLM** → https://notebooklm.google.com/
3. **Sync document** → Click sync button
4. **Ask AI questions** → About archived content

## 🛠️ Common Commands

```bash
# Test connections
python -m src.main --test

# Run archiver
python -m src.main

# Debug mode
python -m src.main --debug

# View logs
tail -f data/logs/archiver.log
```

## ❗ Important Notes

- **Manual sync required** in NotebookLM after archiving
- **Keep app running** for continuous archiving
- **Check logs** if something goes wrong
- **Restart** if database gets locked
