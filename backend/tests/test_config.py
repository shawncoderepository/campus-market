import pytest
from pydantic import ValidationError

from application.common.config import ServerConfig, config, load_config, replace_env_variables


def test_replace_env_variables_uses_value_and_default(monkeypatch) -> None:
    monkeypatch.setenv("TEMPLATE_TEST_VALUE", "configured")
    result = replace_env_variables(
        {
            "configured_value": "${TEMPLATE_TEST_VALUE:fallback}",
            "default_value": "${TEMPLATE_MISSING_VALUE:fallback}",
        }
    )
    assert result == {"configured_value": "configured", "default_value": "fallback"}


def test_default_infrastructure_config_is_present_and_disabled() -> None:
    assert config.server.host == "0.0.0.0"
    assert config.server.port == 8000
    assert config.server.reload is True
    assert config.database.enabled is False
    assert config.database.backend == "mysql"
    assert config.redis.enabled is False
    assert config.redis.max_connections == 20


def test_load_config_reads_explicit_yaml_file(monkeypatch) -> None:
    monkeypatch.setenv("CONFIG_FILE", "config-example.yaml")
    assert load_config().project_name == "orbai-fastapi-template"


def test_load_config_rejects_non_yaml_file(monkeypatch) -> None:
    monkeypatch.setenv("CONFIG_FILE", "README.md")
    with pytest.raises(ValueError, match="Only YAML"):
        load_config()


def test_load_config_explains_how_to_create_missing_config(monkeypatch) -> None:
    monkeypatch.setenv("CONFIG_FILE", "config-missing.yaml")
    with pytest.raises(FileNotFoundError, match="cp config-example.yaml config.yaml"):
        load_config()


def test_server_port_must_be_valid() -> None:
    with pytest.raises(ValidationError):
        ServerConfig(port=70000)
