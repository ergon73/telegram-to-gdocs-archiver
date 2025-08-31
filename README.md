# Telegram to Google Docs Archiver

🚀 **Production-ready Python application** that archives Telegram messages to Google Docs for NotebookLM integration with enhanced formatting and robust error handling.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telethon](https://img.shields.io/badge/Telethon-1.34.0-blue.svg)](https://github.com/LonamiWebs/Telethon)
[![Google Docs API](https://img.shields.io/badge/Google%20Docs%20API-v1-green.svg)](https://developers.google.com/docs/api)

## ✨ Features

- 🔄 **Real-time archiving** of Telegram channel messages
- 📝 **Batch processing** for efficient Google Docs updates
- 🔗 **Forward handling** with metadata preservation
- 💾 **State persistence** between restarts
- 🛡️ **Error recovery** with retry logic and graceful shutdown
- 📊 **Comprehensive logging** and monitoring
- 🎨 **Rich text formatting** in Google Docs (colors, bold, italic)
- 🔗 **Smart link processing** with URL cleaning and Markdown support
- 📱 **Media support** (photos, documents with captions)
- 🚀 **Enhanced forward processing** (users and channels)
- 🛠️ **Database recovery** from corruption
- ⚡ **Graceful shutdown** with signal handling

## 🎯 Key Improvements

### Enhanced Google Docs Formatting
- **Color-coded headers** and content sections
- **Clickable links** with proper URL cleaning
- **Emoji indicators** for different content types
- **Batch headers/footers** with timestamps
- **Media type indicators** (📷 Photo, 📹 Video, etc.)

### Robust Link Processing
- **Markdown link extraction** `[text](url)`
- **Automatic URL cleaning** removes trailing `).` and fixes malformed URLs
- **Fallback processing** for plain URLs
- **Link validation** and error handling

### Improved Error Handling
- **Graceful shutdown** with SIGINT/SIGTERM handling
- **Database recovery** from corruption (automatic cleanup)
- **Fallback formatting** when Google Docs API fails
- **Enhanced retry mechanisms** with exponential backoff

## 📋 Requirements

- Python 3.11+
- Telegram API credentials
- Google Cloud credentials with Docs API enabled

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/telegram-to-gdocs-archiver.git
cd telegram-to-gdocs-archiver
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp config/.env.example .env
# Edit .env with your credentials
```

### 4. Set up Google Cloud
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Docs API**:
   - Go to APIs & Services → Library
   - Search "Google Docs API"
   - Click Enable
4. Create OAuth 2.0 credentials:
   - Go to APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download JSON file as `credentials.json` to project root

### 5. Get Telegram credentials
1. Visit [my.telegram.org/apps](https://my.telegram.org/apps)
2. Create application and get API ID/Hash

### 6. Configure .env file
```bash
# Telegram Configuration
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_CHANNEL_ID=-1001234567890
TELEGRAM_SESSION_NAME=archiver_bot

# Google Configuration  
GOOGLE_DOC_ID=your_google_doc_id_here
GOOGLE_CREDENTIALS_PATH=credentials.json

# Processing Configuration
BATCH_SIZE=5
CHECK_INTERVAL=30
MAX_RETRIES=3
```

### 7. Run the application
```bash
# Test connections
python -m src.main --test

# Run archiver
python -m src.main

# Debug mode
python -m src.main --debug
```

## 🔧 Configuration

### Finding Channel ID

For private channels, forward any message to [@userinfobot](https://t.me/userinfobot) to get the channel ID.

### Google Doc ID

1. Open your Google Doc
2. Copy the ID from URL: `https://docs.google.com/document/d/[THIS_IS_THE_ID]/edit`

## 📝 NotebookLM Integration

### ⚠️ Important: Manual Synchronization Required

**NotebookLM does not automatically sync with Google Docs.** After the archiver saves messages to your Google Doc, you need to manually sync it in NotebookLM:

1. **Open NotebookLM** (https://notebooklm.google.com/)
2. **Go to your document** that's being archived
3. **Click "Sync"** or refresh the document
4. **Wait for sync completion**
5. **Now you can ask AI questions** about the archived content

### What Gets Archived

The application archives:
- ✅ **Message text** from forwarded messages
- ✅ **Original links** from messages (cleaned and clickable)
- ✅ **Forward metadata** (source channel, original date)
- ✅ **Media captions** (for photos/documents)
- ✅ **Timestamps** and source information
- ✅ **Rich formatting** (colors, bold, italic)

### Format in Google Docs

Messages are formatted with enhanced styling:
- **Header**: `[2025-08-31 09:00:00] | 📢 ChannelName` (bold, colored)
- **Forward info**: `↪️ Forwarded from: OriginalChannel` (italic, colored)
- **Content**: The actual message text
- **Links**: `🔗 View in Telegram` (clickable, colored)
- **Media**: `📷 Photo: caption` (bold, colored)
- **Separator**: `══════════════════════════════════════`

## 🔧 Troubleshooting

### Common Issues and Solutions

1. **Google Auth Error**
   ```bash
   # Delete token and re-authenticate
   rm data/state/token.pickle
   python -m src.main
   ```

2. **Telegram Session Error**
   ```bash
   # Delete session file and re-authenticate
   rm archiver_bot.session
   python -m src.main
   ```

3. **Database Lock Error**
   - Application automatically handles database corruption
   - Deletes and recreates corrupted database files

4. **Bot Limitations**
   - Bots cannot fetch message history
   - Only listens for new messages

5. **Link Formatting Issues**
   - URLs are automatically cleaned
   - Trailing punctuation removed
   - Malformed URLs fixed

6. **Forward Processing Errors**
   - Enhanced error handling for MessageFwdHeader
   - Proper user and channel forward support

## 📊 Monitoring

### Check application logs
```bash
tail -f data/logs/archiver.log
```

### View statistics
```bash
python -m src.main --test
```

### Monitor in real-time
```bash
# Debug mode with detailed logging
python -m src.main --debug
```

## 📁 Project Structure

```
telegram-to-gdocs-archiver/
├── src/                    # Source code
│   ├── config/            # Configuration management
│   ├── telegram/          # Telegram client and models
│   ├── google/            # Google Docs integration
│   ├── storage/           # State management
│   ├── utils/             # Utilities and helpers
│   └── exceptions/        # Custom exceptions
├── data/                  # Application data
│   ├── state/            # State database
│   └── logs/             # Log files
├── config/               # Configuration files
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── QUICKSTART.md        # Quick setup guide
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for all public methods
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client library
- [Google Docs API](https://developers.google.com/docs/api) - Google Docs integration
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Loguru](https://loguru.readthedocs.io/) - Logging framework

## 📞 Support

For issues and questions:

1. **Check the troubleshooting section** above
2. **Review the logs** in `data/logs/archiver.log`
3. **Search existing issues** on GitHub
4. **Open a new issue** with detailed information

### Issue Template

When opening an issue, please include:

- **Python version**: `python --version`
- **Operating system**: Windows/macOS/Linux
- **Error message**: Full error traceback
- **Steps to reproduce**: Detailed steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happened

## ⭐ Star History

If this project helps you, please give it a ⭐ on GitHub!

---

**Made with ❤️ for the Telegram and NotebookLM community**
