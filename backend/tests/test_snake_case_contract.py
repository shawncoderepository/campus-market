import pytest
from pydantic import ValidationError

from application.common.helper.response_helper import ResponseHelper
from application.common.schema import PageResult, SnakeCaseModel


class ExampleReq(SnakeCaseModel):
    display_name: str


def test_request_model_accepts_snake_case() -> None:
    assert ExampleReq.model_validate({"display_name": "demo"}).display_name == "demo"


def test_request_model_rejects_camel_case() -> None:
    with pytest.raises(ValidationError):
        ExampleReq.model_validate({"displayName": "demo"})


def test_schema_declaration_rejects_non_snake_case_field() -> None:
    with pytest.raises(TypeError, match="snake_case"):

        class InvalidResponse(SnakeCaseModel):
            displayName: str


def test_response_helper_rejects_dictionary_data() -> None:
    with pytest.raises(TypeError, match="Pydantic BaseModel"):
        ResponseHelper.success({"displayName": "demo"})
    with pytest.raises(TypeError, match="Pydantic BaseModel"):
        ResponseHelper.error(data={"error_detail": "demo"})


def test_page_result_uses_snake_case_page_size() -> None:
    result = PageResult[str](list=["item"], total=1, page=1, page_size=20)
    assert result.model_dump() == {
        "list": ["item"],
        "total": 1,
        "page": 1,
        "page_size": 20,
    }


def test_openapi_properties_use_snake_case() -> None:
    from application import create_app

    schema = create_app().openapi()
    for component in schema.get("components", {}).get("schemas", {}).values():
        for property_name in component.get("properties", {}):
            assert property_name == property_name.lower()
            assert "-" not in property_name
