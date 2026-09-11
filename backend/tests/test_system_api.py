import json

from fastapi.testclient import TestClient

from application import create_app
from application.common.helper import ResponseHelper


def test_health_response_uses_standard_envelope_and_snake_case() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/health", headers={"x-request-id": "test-request-id"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request-id"
    assert response.json() == {
        "code": 0,
        "message": "成功",
        "data": {
            "service_name": "orbai-fastapi-template",
            "service_status": "ok",
        },
    }


def test_version_response() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/version")
    assert response.status_code == 200
    assert response.json()["data"]["version"] == "0.1.0"


def test_error_response_keeps_the_same_envelope() -> None:
    response = ResponseHelper.error(code=40400, message="资源不存在")
    assert response.status_code == 200
    assert json.loads(response.body) == {
        "code": 40400,
        "message": "资源不存在",
        "data": None,
    }
