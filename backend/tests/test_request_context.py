from fastapi import APIRouter
from fastapi.testclient import TestClient

from application import create_app
from application.common.schema import SnakeCaseModel
from application.middleware import get_request_context, get_request_context_or_none


class RequestContextRes(SnakeCaseModel):
    request_id: str
    language: str
    client_ip: str
    user_agent: str


def test_request_context_extracts_headers() -> None:
    app = create_app()
    router = APIRouter()

    @router.get("/test-context")
    async def context_data() -> RequestContextRes:
        context = get_request_context()
        return RequestContextRes(
            request_id=context.request_id,
            language=context.language,
            client_ip=context.client_ip,
            user_agent=context.user_agent,
        )

    app.include_router(router)
    with TestClient(app) as client:
        response = client.get(
            "/test-context",
            headers={
                "x-request-id": "request-123",
                "accept-language": "en-US,en;q=0.8",
                "x-forwarded-for": "1.2.3.4, 5.6.7.8",
                "user-agent": "template-test",
            },
        )
    assert response.json() == {
        "request_id": "request-123",
        "language": "en-US",
        "client_ip": "1.2.3.4",
        "user_agent": "template-test",
    }
    assert get_request_context_or_none() is None
