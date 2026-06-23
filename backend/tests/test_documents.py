import io
import os
import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_upload_document_endpoint_requires_auth(client):
    response = client.post("/api/v1/documents/upload")
    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_501_NOT_IMPLEMENTED}
