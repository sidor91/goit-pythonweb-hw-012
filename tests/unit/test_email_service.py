import pytest

from src.services.email import service as email_service


class DummyFastMail:
    def __init__(self, config):
        self.config = config

    async def send_message(self, message, template_name=None):
        return {"status": "ok", "template": template_name}


@pytest.mark.asyncio
async def test_send_email_with_fastmail(monkeypatch):
    monkeypatch.setattr(email_service, "FastMail", DummyFastMail)

    result = await email_service.send_email(
        "test@example.com", "tester", "http://localhost"
    )
    assert result is None


@pytest.mark.asyncio
async def test_send_password_reset_email_with_fastmail(monkeypatch):
    monkeypatch.setattr(email_service, "FastMail", DummyFastMail)

    result = await email_service.send_password_reset_email(
        "test@example.com", "tester", "http://localhost"
    )
    assert result is None
