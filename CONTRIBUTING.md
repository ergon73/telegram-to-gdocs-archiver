# Contributing to Telegram to Google Docs Archiver

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs
- Use the [issue template](.github/ISSUE_TEMPLATE.md)
- Provide detailed steps to reproduce
- Include error messages and logs
- Specify your environment (OS, Python version)

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Consider implementation complexity

### Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📋 Development Guidelines

### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use type hints for all function signatures
- Add docstrings for all public methods
- Keep functions small and focused

### Testing
- Write tests for new features
- Ensure all tests pass before submitting PR
- Add integration tests for critical functionality

### Documentation
- Update README.md if adding new features
- Add docstrings for new functions
- Update configuration examples if needed

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- Git
- Virtual environment (recommended)

### Setup Steps
```bash
# Clone your fork
git clone https://github.com/yourusername/telegram-to-gdocs-archiver.git
cd telegram-to-gdocs-archiver

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_specific.py
```

### Code Quality Checks
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 📝 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No sensitive data is included
- [ ] Changes are focused and minimal

### PR Description
- Describe the changes made
- Link to related issues
- Include screenshots for UI changes
- Mention any breaking changes

### Review Process
- Maintainers will review your PR
- Address any feedback or requested changes
- PRs will be merged once approved

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 📞 Getting Help

- Check existing issues and discussions
- Join our community discussions
- Contact maintainers for urgent issues

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to the Telegram to Google Docs Archiver project!
