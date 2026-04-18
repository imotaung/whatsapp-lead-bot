import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_landing():
    response = client.get("/")
    assert response.status_code == 200
    assert "WhatsApp" in response.text

@patch("app.main.rate_limiter.is_allowed", return_value=True)
@patch("app.main.sheets_client.append_lead")
def test_webhook_success(mock_sheets, mock_rate):
    response = client.post("/webhook", data={
        "Body": "Hello", "From": "whatsapp:+123", "To": "whatsapp:+456"
    })
    assert response.status_code == 200
    assert "Thank you" in response.text
    mock_sheets.assert_called_once()