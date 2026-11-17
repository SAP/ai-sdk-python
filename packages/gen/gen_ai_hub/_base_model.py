"""
Shared base model and response-validation helpers for all `gen_ai_hub models.

The `SdkBaseModel` sets `extra="forbid"`, which rejects unknown parameters during validation. 
The `validate_response` and `validate_response_as` helpers overwrite this setting to `extra="allow"`
for response validation.
"""

from typing import Any, Type, TypeVar

from pydantic import BaseModel, ConfigDict, TypeAdapter

T = TypeVar("T", bound=BaseModel)


class SdkBaseModel(BaseModel):
    """
    Abstract base model that extends Pydantic's BaseModel.

    - `extra="forbid"` prevents unexpected fields from being accepted or sent,
      since the external API is strict about allowed parameters.
    - `exclude_none=True` ensures optional fields that were not provided are
      omitted from the payload instead of being serialized as None.
    - `by_alias=True` guarantees aliases are used during serialization, which is
      required because some API field names conflict with Pydantic's built-ins.

    This enforces consistent and safe serialization behavior across all
    derived models.
    """
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
    )

    def model_dump(self, **kwargs):
        """Dumps the model to a dictionary with default settings."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


def validate_response(model: Type[T], data: Any) -> T:
    """Validate a response payload into `model`.

    Sets the `extra=allow` flag, which includes unknown fields into the model.

    Args:
        model: A :class:`pydantic.BaseModel` subclass to validate into.
        data: The response payload to validate.

    Returns:
        An instance of ``model``.
    """
    return model.model_validate(data, extra="allow")


def validate_response_as(type_: Any, data: Any) -> Any:
    """Validate a response payload into an arbitrary type.

    Only use this for types that cannot be validated via `validate_response`.

    Args:
        type_: Any type accepted by :class:`pydantic.TypeAdapter`.
        data: The response payload to validate.

    Returns:
        The validated value.
    """
    return TypeAdapter(type_).validate_python(data, extra="allow")
