from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_request_id_and_exception_handler() -> None:
    app = create_app()

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    client = TestClient(app)
    response = client.get("/boom", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "req-123"
    assert response.json() == {
        "error": "internal_server_error",
        "request_id": "req-123",
    }
