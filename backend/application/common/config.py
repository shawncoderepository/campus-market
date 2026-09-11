import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


class DocConfig(BaseModel):
    docs_url: str = "/docs"
    enable_docs: bool = True
    redoc_url: str = "/redoc"
    enable_redoc: bool = True


class LogConfig(BaseModel):
    level: str = "INFO"


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    reload: bool = False


class CorsConfig(BaseModel):
    allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = False
    allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])


class DatabaseConfig(BaseModel):
    enabled: bool = False
    backend: str = "mysql"
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    name: str = "orbai_template"
    charset: str = "utf8mb4"
    minsize: int = 1
    maxsize: int = 10
    echo: bool = False
    auto_generate_schema: bool = False
    sqlite_path: str = "data/app.sqlite3"
    use_tz: bool = False
    timezone: str = "Asia/Shanghai"

    @model_validator(mode="after")
    def validate_database(self) -> "DatabaseConfig":
        if self.backend not in {"mysql", "sqlite"}:
            raise ValueError("database.backend must be 'mysql' or 'sqlite'")
        if self.minsize < 1 or self.maxsize < self.minsize:
            raise ValueError("database pool size must satisfy 1 <= minsize <= maxsize")
        return self


class JwtConfig(BaseModel):
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7


class LlmConfig(BaseModel):
    enabled: bool = True
    api_base: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    timeout_seconds: float = 30.0


class UploadConfig(BaseModel):
    dir: str = "uploads"
    max_size_mb: int = 5


class RedisConfig(BaseModel):
    enabled: bool = False
    fail_fast: bool = False
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0
    max_connections: int = 20
    socket_connect_timeout: float = 3.0
    socket_timeout: float = 3.0
    key_prefix: str = "orbai"


class Setting(BaseModel):
    debug_mode: bool = False
    project_name: str
    version: str = "0.1.0"
    prefix: str = "/api"
    secret_key: str
    server: ServerConfig = Field(default_factory=ServerConfig)
    doc: DocConfig = Field(default_factory=DocConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    jwt: JwtConfig = Field(default_factory=JwtConfig)
    llm: LlmConfig = Field(default_factory=LlmConfig)
    upload: UploadConfig = Field(default_factory=UploadConfig)


def replace_env_variables(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: replace_env_variables(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_env_variables(item) for item in value]
    if not isinstance(value, str):
        return value

    output = value
    for match in _ENV_PATTERN.findall(value):
        name, separator, default = match.partition(":")
        output = output.replace(f"${{{match}}}", os.getenv(name, default if separator else ""))
    return output


def load_config() -> Setting:
    root_dir = Path(__file__).resolve().parents[2]
    configured_path = os.getenv("CONFIG_FILE", "").strip()
    if configured_path:
        path = Path(configured_path)
        if not path.is_absolute():
            path = root_dir / path
    else:
        env = os.getenv("ENV", "").strip()
        path = root_dir / (f"config-{env}.yaml" if env else "config.yaml")

    if not path.exists():
        raise FileNotFoundError(
            f"YAML config file not found: {path}. "
            "Run `cp config-example.yaml config.yaml` before starting the application."
        )
    if path.suffix not in {".yaml", ".yml"}:
        raise ValueError(f"Only YAML config files are supported: {path}")

    with path.open("r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}
    if not isinstance(raw_config, dict):
        raise ValueError(f"Config must be a YAML mapping: {path}")
    return Setting.model_validate(replace_env_variables(raw_config))


config = load_config()

__all__ = ["config"]
