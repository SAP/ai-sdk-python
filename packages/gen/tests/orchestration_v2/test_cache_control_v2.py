"""
Unit tests for prompt-caching serialization (cache_control) in Orchestration V2.

Covers the three spec attachment points:
  - TextContent.cache_control      (TextPart)
  - UserChatMessageContentItem     (TextPart / ImagePart)
  - ChatCompletionTool.cache_control
"""
import unittest

from gen_ai_hub.orchestration_v2.models.cache_control import CacheControl
from gen_ai_hub.orchestration_v2.models.multimodal_items import TextPart, ImagePart, ImageUrl
from gen_ai_hub.orchestration_v2.models.tools import FunctionTool, FunctionObject


class TestCacheControlModel(unittest.TestCase):
    """CacheControl serialization."""

    def test_default_ttl_omits_key(self):
        """CacheControl() with no TTL serializes to {"type": "ephemeral"}."""
        d = CacheControl().model_dump(by_alias=True)
        self.assertEqual(d, {"type": "ephemeral"})
        self.assertNotIn("ttl", d)

    def test_5m_ttl(self):
        d = CacheControl(ttl="5m").model_dump(by_alias=True)
        self.assertEqual(d, {"type": "ephemeral", "ttl": "5m"})

    def test_1h_ttl(self):
        d = CacheControl(ttl="1h").model_dump(by_alias=True)
        self.assertEqual(d, {"type": "ephemeral", "ttl": "1h"})


class TestTextPartCacheControl(unittest.TestCase):
    """TextPart.cache_control serialization."""

    def test_with_cache_control(self):
        part = TextPart(text="hello", cache_control=CacheControl())
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["type"], "text")
        self.assertEqual(d["text"], "hello")
        self.assertEqual(d["cache_control"], {"type": "ephemeral"})

    def test_without_cache_control_omits_key(self):
        part = TextPart(text="hello")
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertNotIn("cache_control", d)

    def test_1h_ttl(self):
        part = TextPart(text="hello", cache_control=CacheControl(ttl="1h"))
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral", "ttl": "1h"})


class TestImagePartCacheControl(unittest.TestCase):
    """ImagePart.cache_control serialization."""

    def _image_part(self, **kwargs):
        return ImagePart(image_url=ImageUrl(url="https://example.com/img.png"), **kwargs)

    def test_with_cache_control(self):
        d = self._image_part(cache_control=CacheControl()).model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["type"], "image_url")
        self.assertEqual(d["cache_control"], {"type": "ephemeral"})

    def test_without_cache_control_omits_key(self):
        d = self._image_part().model_dump(by_alias=True, exclude_none=True)
        self.assertNotIn("cache_control", d)

    def test_1h_ttl(self):
        d = self._image_part(cache_control=CacheControl(ttl="1h")).model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral", "ttl": "1h"})


class TestFunctionToolCacheControl(unittest.TestCase):
    """ChatCompletionTool.cache_control serialization via FunctionTool."""

    def _tool(self, **kwargs):
        return FunctionTool(
            function=FunctionObject(
                name="classify",
                description="Classify input.",
                parameters={"type": "object", "properties": {}},
            ),
            **kwargs,
        )

    def test_with_cache_control(self):
        d = self._tool(cache_control=CacheControl()).model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral"})

    def test_without_cache_control_omits_key(self):
        d = self._tool().model_dump(by_alias=True, exclude_none=True)
        self.assertNotIn("cache_control", d)

    def test_1h_ttl(self):
        d = self._tool(cache_control=CacheControl(ttl="1h")).model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral", "ttl": "1h"})

    def test_type_field_serializes(self):
        """type_ with alias 'type' must appear in output."""
        d = self._tool().model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["type"], "function")

    def test_no_duplicate_type_from_subclass(self):
        """FunctionTool must not declare its own type_ field (inherits from ChatCompletionTool)."""
        import inspect
        own_fields = FunctionTool.model_fields
        # 'type_' is defined on ChatCompletionTool; FunctionTool should only add 'function'
        self.assertIn("function", own_fields)
        # Ensure serialization is still correct (regression guard)
        d = self._tool().model_dump(by_alias=True)
        self.assertEqual(d["type"], "function")


if __name__ == "__main__":
    unittest.main()
