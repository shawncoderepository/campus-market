import re

from pydantic import BaseModel, ConfigDict

_SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


class SnakeCaseModel(BaseModel):
    """Strict base model for request and response DTOs.

    Fields must be declared in snake_case. Unknown request keys, including
    camelCase alternatives, are rejected instead of being silently ignored.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        annotations = getattr(cls, "__annotations__", {})
        invalid_names = [name for name in annotations if not _SNAKE_CASE_PATTERN.fullmatch(name)]
        if invalid_names:
            joined = ", ".join(invalid_names)
            raise TypeError(f"Schema fields must use snake_case: {joined}")
