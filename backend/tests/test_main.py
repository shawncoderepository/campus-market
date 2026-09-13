from unittest.mock import Mock

import main


def test_run_uses_yaml_server_config(monkeypatch) -> None:
    uvicorn_run = Mock()
    monkeypatch.setattr(main.uvicorn, "run", uvicorn_run)
    main.run()
    uvicorn_run.assert_called_once_with("main:app", host="0.0.0.0", port=8001, reload=True)
