# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced Google Docs formatting with colors and emojis
- Smart link processing with URL cleaning
- Graceful shutdown with signal handling
- Database recovery from corruption
- Enhanced forward processing for users and channels

### Changed
- Improved error handling with fallback mechanisms
- Updated Google Docs API integration
- Enhanced logging and monitoring

### Fixed
- MessageFwdHeader attribute errors
- URL formatting issues with trailing punctuation
- Database lock errors
- Google Docs API color structure issues

## [1.0.0] - 2025-08-31

### Added
- Initial release
- Telegram message archiving to Google Docs
- Batch processing for efficient updates
- State persistence between restarts
- Forward handling with metadata
- Basic error recovery and retry logic
- Comprehensive logging
- NotebookLM integration support

### Features
- Real-time message archiving
- Rich text formatting in Google Docs
- Link preservation from forwarded messages
- Media support (photos, documents with captions)
- Configuration management with Pydantic
- CLI interface with Click
- Virtual environment support

---

## Version History

### v1.0.0 (Initial Release)
- Basic functionality for archiving Telegram messages
- Google Docs integration
- State management
- Error handling

### v2.0.0 (Enhanced Features)
- Pydantic v2 compatibility
- Database recovery mechanisms
- Improved error handling

### v3.0.0 (Production Ready)
- Enhanced Google Docs formatting
- Robust link processing
- Graceful shutdown
- Comprehensive error recovery
- Enhanced forward processing

## Contributing

To add entries to this changelog:

1. Add your changes under the appropriate section
2. Use the following categories:
   - **Added**: New features
   - **Changed**: Changes in existing functionality
   - **Deprecated**: Soon-to-be removed features
   - **Removed**: Removed features
   - **Fixed**: Bug fixes
   - **Security**: Vulnerability fixes

3. Follow the existing format and style
4. Include issue numbers when applicable
