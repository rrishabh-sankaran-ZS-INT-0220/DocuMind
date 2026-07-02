import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend.app.api.v1 import auth as auth_api
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_google_callback_rejects_mismatched_state(client, monkeypatch):
    def fail_exchange(*args, **kwargs):
        raise AssertionError("exchange_code_and_get_userinfo should not be called")

    monkeypatch.setattr(auth_api, "exchange_code_and_get_userinfo", fail_exchange)

    login_response = client.post(
        "/api/v1/auth/google/login",
        json={"provider": "google"},
    )
    assert login_response.status_code == status.HTTP_200_OK

    response = client.get(
        "/api/v1/auth/google/callback",
        params={"code": "test-code", "state": "mismatched-state"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid OAuth state"
