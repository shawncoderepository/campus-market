import uvicorn

from application import app as app
from application.common.config import config


def run() -> None:
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
    )


if __name__ == "__main__":
    run()
