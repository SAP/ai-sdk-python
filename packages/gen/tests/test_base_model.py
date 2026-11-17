"""Tests for the shared base model and response-validation helpers.

In particular, these cover the handling of extra parameters during validation dictated by `_base_model`:

- `SdkBaseModel` enforces ``extra="forbid"``
- `validate_response` and `validate_response_as` override this to ``extra="allow"``
"""

import unittest
from typing import Optional

from pydantic import ValidationError

from gen_ai_hub._base_model import (
    SdkBaseModel,
    validate_response,
    validate_response_as,
)


class Nested(SdkBaseModel):
    value: int


class Example(SdkBaseModel):
    name: str
    count: Optional[int] = None
    nested: Optional[Nested] = None
    items: Optional[list[Nested]] = None


class TestSdkBaseModel(unittest.TestCase):
    """SdkBaseModel rejects unknown fields."""

    def test_rejects_unknown_fields(self):
        with self.assertRaises(ValidationError):
            Example(name="a", unexpected="boom")

    def test_accepts_known_fields(self):
        model = Example(name="a", count=3)
        self.assertEqual(model.name, "a")
        self.assertEqual(model.count, 3)

    def test_model_dump_excludes_none_by_default(self):
        self.assertEqual(Example(name="a").model_dump(), {"name": "a"})

    def test_model_dump_overrides_still_apply(self):
        dumped = Example(name="a").model_dump(exclude_none=False)
        self.assertIn("count", dumped)
        self.assertIsNone(dumped["count"])


class TestValidateResponse(unittest.TestCase):
    """validate_response retains unknown fields at every nesting depth."""

    def test_retains_unknown_fields(self):
        response = validate_response(Example, {"name": "a", "surprise": "kept"})
        self.assertEqual(response.name, "a")
        self.assertEqual(response.surprise, "kept")

    def test_retains_unknown_fields_in_nested_model(self):
        response = validate_response(Example, {
            "name": "a",
            "nested": {"value": 1, "nested_extra": "kept"},
        })
        self.assertEqual(response.nested.value, 1)
        self.assertEqual(response.nested.nested_extra, "kept")

    def test_extra_fields_survive_deeper_nesting(self):
        """Unknown fields must be retained at the top level, inside a nested
        model, and inside each element of a nested list of models."""
        response = validate_response(Example, {
            "name": "a",
            "nested": {"value": 1, "nested_extra": "N"},
            "items": [
                {"value": 2, "item_extra": "I0"},
                {"value": 3, "item_extra": "I1"},
            ],
            "top_extra": "T",
        })
        self.assertEqual(response.top_extra, "T")
        self.assertEqual(response.nested.nested_extra, "N")
        self.assertEqual(response.items[0].item_extra, "I0")
        self.assertEqual(response.items[1].item_extra, "I1")

    def test_still_validates_known_fields(self):
        with self.assertRaises(ValidationError):
            validate_response(Example, {"name": "a", "count": "not-an-int"})


class TestValidateResponseAs(unittest.TestCase):
    """validate_response_as handles types TypeAdapter supports (e.g. lists)."""

    def test_validates_list_of_models_and_retains_extra(self):
        result = validate_response_as(list[Example], [
            {"name": "a", "surprise": "kept"},
            {"name": "b"},
        ])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].surprise, "kept")
        self.assertEqual(result[1].name, "b")

    def test_still_validates_known_fields(self):
        with self.assertRaises(ValidationError):
            validate_response_as(list[Example], [{"name": "a", "count": "nope"}])
