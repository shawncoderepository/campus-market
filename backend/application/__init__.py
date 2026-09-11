from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from application.apis import register_routes
from application.common.config import config
from application.common.exception.handlers import register_exception_handlers
from application.core.lifespan import lifespan
from application.middleware import RequestContextMiddleware


def create_app() -> FastAPI:
    """Application factory used by production startup and tests."""
    app = FastAPI(
        debug=config.debug_mode,
        lifespan=lifespan,
        title=config.project_name,
        version=config.version,
        docs_url=(f"{config.prefix}{config.doc.docs_url}" if config.doc.enable_docs else None),
        redoc_url=(f"{config.prefix}{config.doc.redoc_url}" if config.doc.enable_redoc else None),
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.allow_methods,
        allow_headers=config.cors.allow_headers,
    )
    register_exception_handlers(app)
    register_routes(app)

    # 挂载上传文件静态目录（商品图片/头像）
    upload_root = Path(__file__).resolve().parents[1] / config.upload.dir
    upload_root.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_root)), name="uploads")
    return app


app = create_app()

__all__ = ["app", "create_app"]
