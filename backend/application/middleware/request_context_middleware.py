from contextvars import ContextVar
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


@dataclass(frozen=True, slots=True)
class RequestContext:
    request_id: str
    language: str
    client_ip: str
    user_agent: str


_request_context: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else ""
        if not client_ip and request.client:
            client_ip = request.client.host
        context = RequestContext(
            request_id=request.headers.get("x-request-id", str(uuid4())),
            language=request.headers.get("accept-language", "zh-CN").split(",")[0].strip(),
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", "").strip(),
        )
        token = _request_context.set(context)
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = context.request_id
            return response
        finally:
            _request_context.reset(token)


def get_request_context() -> RequestContext:
    context = _request_context.get()
    if context is None:
        raise RuntimeError("Request context is only available during a request")
    return context


def get_request_context_or_none() -> RequestContext | None:
    return _request_context.get()
