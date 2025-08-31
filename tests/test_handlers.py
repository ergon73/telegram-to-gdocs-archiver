"""Тесты для обработчика сообщений Telegram."""
import pytest
from src.telegram.models import TelegramMessage
from src.telegram.handlers import handle_new_message
import asyncio

@pytest.mark.asyncio
async def test_handle_new_message():
    class DummyMsg:
        id = 1
        date = "2025-08-31"
        sender_id = 12345
        text = "Test message"
        def to_dict(self):
            return {"id": 1, "date": "2025-08-31", "sender_id": 12345, "text": "Test message"}

    msg = DummyMsg()
    result = await handle_new_message(msg)
    assert isinstance(result, TelegramMessage)
    assert result.id == 1
    assert result.text == "Test message"
