import importlib
import inspect
from pathlib import Path

from application.common.schema import SnakeCaseModel


def test_every_api_module_has_a_schema_file() -> None:
    apis_dir = Path(__file__).resolve().parents[1] / "application" / "apis"
    api_files = list(apis_dir.rglob("*_api.py"))
    assert api_files
    for api_file in api_files:
        assert (api_file.parent / "schema.py").is_file(), (
            f"API module {api_file.parent.name} must contain schema.py"
        )


def test_api_schema_classes_use_req_or_res_suffix() -> None:
    apis_dir = Path(__file__).resolve().parents[1] / "application" / "apis"
    schema_files = list(apis_dir.rglob("schema.py"))
    assert schema_files
    for schema_file in schema_files:
        relative_module = schema_file.relative_to(apis_dir.parents[1]).with_suffix("")
        module_name = ".".join(relative_module.parts)
        module = importlib.import_module(module_name)
        schema_classes = [
            value
            for value in vars(module).values()
            if inspect.isclass(value)
            and value.__module__ == module_name
            and issubclass(value, SnakeCaseModel)
        ]
        assert schema_classes, f"No Pydantic schemas found in {schema_file}"
        for schema_class in schema_classes:
            assert schema_class.__name__.endswith(("Req", "Res")), (
                f"{schema_class.__name__} must end with Req or Res"
            )
