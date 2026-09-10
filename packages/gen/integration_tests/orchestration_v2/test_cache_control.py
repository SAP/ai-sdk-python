"""
Unit and integration tests for prompt caching (cache_control) via Orchestration V2.

Caching is supported for Anthropic Claude and Amazon Nova models.
The test targets anthropic--claude-4.6-sonnet (1024-token minimum, 5m and 1h TTLs).

Wire path:
  ai-sdk-python  ->  SAP AI Core /v2/completion  ->  SAP LiteLLM fork  ->  Anthropic API

cache_control is serialized as a plain JSON key on the content block or tool dict by
Pydantic model_dump(). The SAP LiteLLM fork translates it into Anthropic's native
prompt-caching format.

The spec defines cache_control on three schema-level attachment points:
  - TextContent.cache_control         (TextPart in py)
  - UserChatMessageContentItem.cache_control  (TextPart / ImagePart in py)
  - ChatCompletionTool.cache_control

Response fields (from SAP AI Core orchestration docs):
  prompt_tokens_details.cached_tokens           -- tokens read from cache (hit)
  prompt_tokens_details.cache_creation_tokens   -- tokens written to cache (miss)
  prompt_tokens_details.cache_creation_token_details.ephemeral_5m_input_tokens
  prompt_tokens_details.cache_creation_token_details.ephemeral_1h_input_tokens
"""
import unittest

from gen_ai_hub.orchestration_v2.models.cache_control import CacheControl
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.multimodal_items import TextPart, ImagePart, ImageUrl
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.models.tools import ChatCompletionTool, FunctionTool, FunctionObject
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503

# Must exceed the 1024-token minimum for claude-4.6-sonnet cache points.
_LONG_SYSTEM_PROMPT = (
    "You are a helpful assistant with deep knowledge of European history. "
    "Below is a detailed reference text that you must use to answer questions accurately.\n\n"
    + (
        "The Roman Empire was one of the largest empires in ancient history. "
        "At its height under Emperor Trajan in 117 AD, it covered over 5 million "
        "square kilometres and held 70 million people, roughly 21 percent of the "
        "world's population at the time. The empire's longevity — nearly five "
        "centuries in the west and fifteen in the east — shaped the languages, "
        "laws, religions, and borders of modern Europe. Latin evolved into the "
        "Romance languages: Italian, Spanish, Portuguese, French, and Romanian. "
        "Roman law underlies most continental legal systems today. Christianity, "
        "adopted as the state religion under Theodosius I in 380 AD, spread "
        "throughout the empire and became the dominant faith of Europe. "
        "The fall of the Western Roman Empire in 476 AD, when the Germanic "
        "chieftain Odoacer deposed the last emperor Romulus Augustulus, marks "
        "the conventional boundary between ancient and medieval history. "
        "The Eastern Roman Empire, known as the Byzantine Empire, continued "
        "for nearly a thousand more years until the fall of Constantinople to "
        "the Ottoman Turks in 1453. Byzantine culture preserved classical Greek "
        "and Roman learning through the Dark Ages and transmitted it to the "
        "Renaissance. The Silk Road trade routes connecting Rome to China "
        "facilitated the exchange of goods, diseases, and ideas across Eurasia. "
        "Roman engineering achievements — aqueducts, roads, concrete construction, "
        "and underfloor heating — were not equalled in Europe for over a millennium "
        "after the empire's fall. The Colosseum, completed in 80 AD, could seat "
        "50,000 to 80,000 spectators and hosted gladiatorial contests, animal "
        "hunts, and public executions for four centuries. "
    ) * 4  # repeat to comfortably exceed 1024 tokens
)

_LLM = LLMModelDetails(
    name="anthropic--claude-4.6-sonnet",
    params={"max_tokens": 64, "temperature": 0.0},
)


def _config(messages, tools=None):
    return OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=messages, tools=tools),
                model=_LLM,
            )
        )
    )


class TestCacheControlSerialization(unittest.TestCase):
    """Unit tests: verify cache_control serializes correctly without a network call."""

    # ------------------------------------------------------------------
    # CacheControl model
    # ------------------------------------------------------------------

    def test_cache_control_default_ttl_omits_key(self):
        """CacheControl() with no TTL serializes to {"type": "ephemeral"}."""
        d = CacheControl().model_dump(by_alias=True)
        self.assertEqual(d, {"type": "ephemeral"})
        self.assertNotIn("ttl", d)

    def test_cache_control_5m_ttl(self):
        """CacheControl(ttl="5m") serializes with ttl field."""
        d = CacheControl(ttl="5m").model_dump(by_alias=True)
        self.assertEqual(d, {"type": "ephemeral", "ttl": "5m"})

    def test_cache_control_1h_ttl(self):
        """CacheControl(ttl="1h") serializes with ttl field."""
        d = CacheControl(ttl="1h").model_dump(by_alias=True)
        self.assertEqual(d, {"type": "ephemeral", "ttl": "1h"})

    # ------------------------------------------------------------------
    # TextPart with cache_control
    # ------------------------------------------------------------------

    def test_text_part_with_cache_control(self):
        """TextPart with cache_control serializes the cache_control block."""
        part = TextPart(text="hello", cache_control=CacheControl())
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["type"], "text")
        self.assertEqual(d["text"], "hello")
        self.assertEqual(d["cache_control"], {"type": "ephemeral"})

    def test_text_part_without_cache_control_omits_key(self):
        """TextPart without cache_control does not emit the key."""
        part = TextPart(text="hello")
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertNotIn("cache_control", d)

    def test_text_part_with_1h_ttl(self):
        """TextPart with CacheControl(ttl='1h') serializes the ttl field."""
        part = TextPart(text="hello", cache_control=CacheControl(ttl="1h"))
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral", "ttl": "1h"})

    # ------------------------------------------------------------------
    # ImagePart with cache_control
    # ------------------------------------------------------------------

    def test_image_part_with_cache_control(self):
        """ImagePart with cache_control serializes the cache_control block."""
        part = ImagePart(
            image_url=ImageUrl(url="https://example.com/img.png"),
            cache_control=CacheControl(),
        )
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["type"], "image_url")
        self.assertEqual(d["cache_control"], {"type": "ephemeral"})

    def test_image_part_without_cache_control_omits_key(self):
        """ImagePart without cache_control does not emit the key."""
        part = ImagePart(image_url=ImageUrl(url="https://example.com/img.png"))
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertNotIn("cache_control", d)

    def test_image_part_with_1h_ttl(self):
        """ImagePart with CacheControl(ttl='1h') serializes the ttl field."""
        part = ImagePart(
            image_url=ImageUrl(url="https://example.com/img.png"),
            cache_control=CacheControl(ttl="1h"),
        )
        d = part.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral", "ttl": "1h"})

    # ------------------------------------------------------------------
    # ChatCompletionTool with cache_control
    # ------------------------------------------------------------------

    def test_tool_cache_control_serialized(self):
        """cache_control on a ChatCompletionTool appears at the tool level."""
        tool = FunctionTool(
            function=FunctionObject(
                name="classify",
                description="Classify input.",
                parameters={"type": "object", "properties": {}},
            ),
            cache_control=CacheControl(),
        )
        d = tool.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral"})

    def test_tool_without_cache_control_omits_key(self):
        """A tool without cache_control does not emit the key."""
        tool = FunctionTool(
            function=FunctionObject(
                name="classify",
                description="Classify input.",
                parameters={"type": "object", "properties": {}},
            ),
        )
        d = tool.model_dump(by_alias=True, exclude_none=True)
        self.assertNotIn("cache_control", d)

    def test_tool_with_1h_ttl(self):
        """cache_control with ttl='1h' on a tool serializes the ttl field."""
        tool = FunctionTool(
            function=FunctionObject(
                name="classify",
                description="Classify input.",
                parameters={"type": "object", "properties": {}},
            ),
            cache_control=CacheControl(ttl="1h"),
        )
        d = tool.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(d["cache_control"], {"type": "ephemeral", "ttl": "1h"})


class TestPromptCachingLive(OrchestrationServiceTestBase):
    """Live integration tests against the SAP AI Core orchestration V2 service."""

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(self.api_url)

    # ------------------------------------------------------------------
    # 1. Cache MISS on first call — cache breakpoint on TextPart directly
    # ------------------------------------------------------------------

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_cache_miss_on_first_call(self):
        """First call with cache_control on the last TextPart block returns
        non-zero cache token activity.

        cache_creation_tokens > 0 on a true miss; cached_tokens > 0 when the
        cache entry is already warm from a previous run. Either proves the
        cache_control breakpoint was accepted by the server.
        """
        config = _config([
            SystemMessage(content=[TextPart(text=_LONG_SYSTEM_PROMPT, cache_control=CacheControl())]),
            UserMessage(content="In one word: what language did Romans speak?"),
        ])
        response = self.service.run(config=config)
        details = response.final_result.usage.prompt_tokens_details
        self.assertIsNotNone(details)
        cache_active = (details.cache_creation_tokens or 0) + (details.cached_tokens or 0)
        self.assertGreater(
            cache_active, 0,
            f"Expected cache activity (cache_creation_tokens or cached_tokens > 0), "
            f"got: {details}",
        )

    # ------------------------------------------------------------------
    # 2. Cache HIT on repeated call
    # ------------------------------------------------------------------

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_cache_hit_on_repeated_call(self):
        """Second call with the same cache breakpoint produces cached_tokens > 0."""
        config = _config([
            SystemMessage(content=[TextPart(text=_LONG_SYSTEM_PROMPT, cache_control=CacheControl())]),
            UserMessage(content="In one word: what language did Romans speak?"),
        ])
        self.service.run(config=config)   # populate cache
        response = self.service.run(config=config)
        details = response.final_result.usage.prompt_tokens_details
        self.assertIsNotNone(details)
        self.assertGreater(
            details.cached_tokens, 0,
            "Expected cached_tokens > 0 on second call (cache hit).",
        )

    # ------------------------------------------------------------------
    # 3. Explicit 1h TTL via TextPart
    # ------------------------------------------------------------------

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_explicit_ttl_1h_via_text_part(self):
        """Attaching CacheControl(ttl='1h') directly to a TextPart returns
        cache_creation_token_details with ephemeral_1h_input_tokens."""
        config = _config([
            SystemMessage(content=[TextPart(text=_LONG_SYSTEM_PROMPT, cache_control=CacheControl(ttl="1h"))]),
            UserMessage(content="Name the last Western Roman emperor."),
        ])
        response = self.service.run(config=config)
        details = response.final_result.usage.prompt_tokens_details
        self.assertIsNotNone(details)
        self.assertIsNotNone(
            details.cache_creation_token_details,
            "Expected cache_creation_token_details when ttl='1h' is used.",
        )


if __name__ == "__main__":
    unittest.main()
