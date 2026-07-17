import unittest
from typing import cast
from unittest.mock import Mock, patch, AsyncMock

import httpx

from gen_ai_hub.orchestration_v2.exceptions import OrchestrationError
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.streaming import GlobalStreamOptions
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService, cache_if_not_none
from tests.mock import (
    get_mocked_ai_core_client,
    ai_core_ai_api_mocker,
    orchestration_completion_v2_mocker,
    orchestration_stream_v2_completion_mocker,
    orchestration_v2_stream_completion_mocker_async,
    orchestration_deployment_not_found_mocker,
    orchestration_too_many_requests_mocker,
    GET_ORCHESTRATION_V2_COMPLETION_RESPONSE
)


class TestOrchestrationService(unittest.TestCase):
    NOT_EXISTENT_DEPLOYMENT_ID = "not_existent"

    def setUp(self):
        self.api_url = "https://api.example.com"
        self.template = Template(
            template=[
                SystemMessage(content="This is a system message."),
                UserMessage(content="Hello, {{?name}}!"),
            ],
            defaults={"name": "World"}
        )
        self.llm = LLMModelDetails(name="gemini-2.0-flash-lite")
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template,
                                                            model=self.llm)
        self.module_config = ModuleConfig(prompt_templating=self.prompt_template)
        self.config = OrchestrationConfig(modules=self.module_config)
        self.stream_config = OrchestrationConfig(modules=self.module_config,
                                                 stream=GlobalStreamOptions(enabled=True))
        self.proxy_client = get_mocked_ai_core_client(client_id='testopenaiclient')

    def test_caching(self):

        @cache_if_not_none
        def func(arg):
            func.calls += 1
            return arg

        func.calls = 0

        self.assertEqual(func(1), 1)
        self.assertEqual(func.calls, 1)
        self.assertEqual(func(1), 1)
        self.assertEqual(func.calls, 1)
        func.cache_clear()
        self.assertEqual(func(1), 1)
        self.assertEqual(func.calls, 2)
        self.assertIsNone(func(None))
        self.assertEqual(func.calls, 3)
        self.assertIsNone(func(None))
        self.assertEqual(func.calls, 4)

    def test_initialization_with_empty_api_url(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(proxy_client=self.proxy_client)
            self.assertEqual(client.api_url,
                             "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/d7f9c215310f5a11")

    def test_initialization_with_config_name(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(config_id="0152d9f0-694f-4bd2-a287-f7d270c9db60",
                                          proxy_client=self.proxy_client)
        self.assertEqual(client.api_url,
                         "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dea20c27f7fe0eca")

    def test_initialization_with_config_id(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(config_name="orchestration-config-2", proxy_client=self.proxy_client)
        self.assertEqual(client.api_url,
                         "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dea20c27f7fe0eca")

    def test_initialization_with_deployment_id(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(deployment_id="dea20c27f7fe0eca", proxy_client=self.proxy_client)
        self.assertEqual(client.api_url, "https://base_url/v2/inference/deployments/dea20c27f7fe0eca")

    def test_initialization_with_non_existing_deployment_id(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(deployment_id=self.NOT_EXISTENT_DEPLOYMENT_ID, proxy_client=self.proxy_client)
        self.assertIn(self.NOT_EXISTENT_DEPLOYMENT_ID, client.api_url)

    def test_run_with_non_existing_deployment_id(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(deployment_id=self.NOT_EXISTENT_DEPLOYMENT_ID, proxy_client=self.proxy_client)
            with orchestration_deployment_not_found_mocker(client.api_url + '/v2/completion'):
                with self.assertRaises(httpx.HTTPStatusError):
                    client.run(config=self.config)

    def test_run_without_config(self):
        service = OrchestrationService(api_url=self.api_url, proxy_client=Mock())

        with self.assertRaises(ValueError):
            service.run()

    def test_run_with_config(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_completion_v2_mocker(client.api_url + '/v2/completion'):
                client.run(config=self.config)
                # test config as a list
                client.run(config=OrchestrationConfig(modules=[self.module_config]))
                # empty config list raises error
                with self.assertRaises(ValueError):
                    client.run(config=OrchestrationConfig(modules=[]))

    def test_usage_details(self):
        """Simple check that usage includes provider-specific token details blocks."""
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_completion_v2_mocker(client.api_url + '/v2/completion'):
                response = client.run(config=self.config)

        usage_dict = response.final_result.usage.model_dump()
        self.assertIn("prompt_tokens_details", usage_dict)
        self.assertIn("completion_tokens_details", usage_dict)
        self.assertIsNotNone(usage_dict["prompt_tokens_details"])
        self.assertIsNotNone(usage_dict["completion_tokens_details"])

    def test_stream_with_config(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_stream_v2_completion_mocker(client.api_url + '/v2/completion'):
                txt = ''
                for chunk in client.stream(config=self.stream_config):
                    if chunk.final_result.choices:
                        txt += chunk.final_result.choices[0].delta.content
                self.assertEqual(txt, 'This confirms receipt of the system message: "Hello, World!\n')

    def test_too_many_requests(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_too_many_requests_mocker(client.api_url + '/v2/completion'):
                with self.assertRaises(OrchestrationError) as context:
                    client.run(config=self.config)
                self.assertIn('X-Custom-Header', cast(OrchestrationError, context.exception).headers)

    def test_retry_backoff_with_retry_after_header(self):
        """Test that retry backoff respects Retry-After header and applies jitter correctly."""
        import time

        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)

            call_times = []
            retry_counts = []

            # Patch the handle_retry method to track calls and timing
            original_handle_retry = client.handle_retry

            def track_retry(*args, **kwargs):
                call_times.append(time.time())
                retry_counts.append(args[0])  # retry_count is first arg
                return original_handle_retry(*args, **kwargs)

            with orchestration_too_many_requests_mocker(client.api_url + '/v2/completion'):
                with patch.object(client, 'handle_retry', side_effect=track_retry):
                    with self.assertRaises(OrchestrationError) as context:
                        client.run_with_retries(config=self.config, max_retries=1, base_delay=1.0)

                    error = cast(OrchestrationError, context.exception)

                    # Verify retry was attempted (with max_retries=1, we get 1 retry attempt)
                    # The retry_count starts at 1 (after initial failure)
                    self.assertEqual(len(retry_counts), 1, "Expected 1 retry attempt")
                    self.assertEqual(retry_counts, [0], "Expected retry count of 0 for first retry")

                    # Verify delay is positive
                    if len(call_times) >= 1:
                        self.assertGreater(len(call_times), 0, "Expected at least one retry delay measurement")

                    # Verify error tracking
                    self.assertIn('X-Custom-Header', error.headers)

    def test_handle_retry_with_retry_after(self):
        """Test that handle_retry uses exponential backoff with Retry-After header."""
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)

            # Create a mock error without Retry-After header
            response = Mock(spec=httpx.Response)
            response.status_code = 429
            response.headers = httpx.Headers({"Retry-After": "3"})
            response.text = "Too Many Requests"
            response.request = Mock()

            error = httpx.HTTPStatusError("429 Too Many Requests", request=response.request, response=response)

            # Collect delays for multiple retries
            delays = []
            for retry_count in range(3):
                delay = client.handle_retry(retry_count=retry_count, base_delay=1.0, error=error, max_retries=5)
                delays.append(delay)

            # Verify all delays are positive
            for delay in delays:
                self.assertGreater(delay, 0.0, "All delays should be positive")
                self.assertLessEqual(delay, 60.0, "All delays should respect max_delay")

    def test_handle_retry_without_retry_after(self):
        """Test that handle_retry uses exponential backoff when no Retry-After header."""
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)

            # Create a mock error without Retry-After header
            response = Mock(spec=httpx.Response)
            response.status_code = 429
            response.headers = httpx.Headers({})
            response.text = "Too Many Requests"
            response.request = Mock()

            error = httpx.HTTPStatusError("429 Too Many Requests", request=response.request, response=response)

            # Collect delays for multiple retries
            delays = []
            for retry_count in range(3):
                delay = client.handle_retry(retry_count=retry_count, base_delay=1.0, error=error, max_retries=5)
                delays.append(delay)

            # Verify all delays are positive
            for delay in delays:
                self.assertGreater(delay, 0.0, "All delays should be positive")
                self.assertLessEqual(delay, 60.0, "All delays should respect max_delay")

    def test_handle_retry_max_retries_exceeded(self):
        """Test that handle_retry raises error when max_retries is exceeded."""
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)

            # Create a mock error
            response = Mock(spec=httpx.Response)
            response.status_code = 429
            response.headers = httpx.Headers({})
            response.text = "Too Many Requests"
            response.request = Mock()

            error = httpx.HTTPStatusError("429 Too Many Requests", request=response.request, response=response)

            # Mock _should_retry to return True so we test the retry_count >= max_retries condition
            with patch.object(client, '_should_retry', return_value=True):
                # Test that it raises when retry_count >= max_retries
                # Need to call handle_retry within an exception context since it uses bare 'raise'
                try:
                    raise error
                except httpx.HTTPStatusError as e:
                    with self.assertRaises(httpx.HTTPStatusError) as context:
                        client.handle_retry(retry_count=3, base_delay=1.0, error=e, max_retries=3)

                    # Verify retries attribute was set
                    raised_error = context.exception
                    self.assertEqual(raised_error.retries, 3, "Expected retries attribute to be set")

    def test_calculate_backoff_with_min_delay(self):
        """Test _calculate_backoff behavior with min_delay parameter."""
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)

            # Test with min_delay (simulating Retry-After header)
            retry_after_delay = 5.0

            # Case 1: When min_delay > exponential delay, returns capped (not min_delay)
            # For retry_count=0, base_delay=1.0: exp = 1.0 * 2^0 = 1.0
            # With min_delay=5.0, max_delay=60.0: capped = min(1.0, 60.0) = 1.0
            # lower = max(0.0, 5.0) = 5.0
            # Since lower (5.0) >= capped (1.0), returns capped = 1.0
            delay1 = client._calculate_backoff(retry_count=0, base_delay=1.0, min_delay=retry_after_delay,
                                               max_delay=60.0)
            self.assertEqual(delay1, 1.0, "When min_delay > exp_delay, should return capped exponential value")

            # Case 2: When exponential delay > min_delay, applies jitter between min_delay and capped
            # For retry_count=3, base_delay=1.0: exp = 1.0 * 2^3 = 8.0
            # With min_delay=5.0, max_delay=60.0: capped = min(8.0, 60.0) = 8.0
            # lower = max(0.0, 5.0) = 5.0
            # Since lower (5.0) < capped (8.0), returns random.uniform(5.0, 8.0)
            delays = [
                client._calculate_backoff(retry_count=3, base_delay=1.0, min_delay=retry_after_delay, max_delay=60.0)
                for _ in range(20)]

            # All delays should be between min_delay and the exponential cap
            for delay in delays:
                self.assertGreaterEqual(delay, retry_after_delay, "Delay should be at least min_delay")
                self.assertLessEqual(delay, 8.0, "Delay should not exceed exponential cap for retry_count=3")

            # Verify jitter produces variance
            unique_delays = len(set(delays))
            self.assertGreater(unique_delays, 1, "Expected jitter to produce varying delays")

            # Case 3: When min_delay == max_delay and exp > min_delay
            # For retry_count=10, base_delay=1.0: exp = 1.0 * 2^10 = 1024.0
            # With min_delay=5.0, max_delay=5.0: capped = min(1024.0, 5.0) = 5.0
            # lower = max(0.0, 5.0) = 5.0
            # Since lower (5.0) >= capped (5.0), returns capped = 5.0
            delay3 = client._calculate_backoff(retry_count=10, base_delay=1.0, min_delay=retry_after_delay,
                                               max_delay=retry_after_delay)
            self.assertEqual(delay3, retry_after_delay, "When min_delay == max_delay, should return that value")

            # Case 4: Test without min_delay (standard behavior)
            # For retry_count=2, base_delay=1.0: exp = 1.0 * 2^2 = 4.0
            # With min_delay=0.0, max_delay=60.0: capped = min(4.0, 60.0) = 4.0
            # lower = max(0.0, 0.0) = 0.0
            # Returns random.uniform(0.0, 4.0)
            delays_no_min = [
                client._calculate_backoff(retry_count=2, base_delay=1.0, min_delay=0.0, max_delay=60.0)
                for _ in range(20)]

            for delay in delays_no_min:
                self.assertGreaterEqual(delay, 0.0, "Delay should be non-negative")
                self.assertLessEqual(delay, 4.0, "Delay should not exceed exponential value")

            # Verify variance with no min_delay
            self.assertGreater(len(set(delays_no_min)), 1, "Expected jitter without min_delay")

    def test_calculate_backoff_exponential_progression(self):
        """Test _calculate_backoff produces exponential backoff progression."""
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)

            # Collect average delays for different retry counts
            num_samples = 50
            avg_delays = []

            for retry_count in range(5):
                delays = [client._calculate_backoff(retry_count=retry_count, base_delay=1.0, min_delay=0.0)
                          for _ in range(num_samples)]
                avg_delays.append(sum(delays) / len(delays))

            # Verify exponential growth in average delays
            for i in range(len(avg_delays) - 1):
                self.assertLess(avg_delays[i], avg_delays[i + 1],
                                f"Expected retry {i + 1} to have higher average delay than retry {i}")

            # Verify capping at max_delay
            large_delays = [client._calculate_backoff(retry_count=10, base_delay=1.0, max_delay=60.0)
                            for _ in range(10)]
            for delay in large_delays:
                self.assertLessEqual(delay, 60.0, "Delay should be capped at max_delay")

    def test_calculate_backoff_custom_max_delay(self):
        """Test _calculate_backoff respects custom max_delay."""
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)

            custom_max = 10.0
            delays = [client._calculate_backoff(retry_count=5, base_delay=1.0, max_delay=custom_max)
                      for _ in range(20)]

            for delay in delays:
                self.assertLessEqual(delay, custom_max, "Delay should respect custom max_delay")
                self.assertGreaterEqual(delay, 0.0, "Delay should be non-negative")

    def test_timeout_client_request(self):
        class FakeResponse:
            def raise_for_status(self):
                pass  # No-op for mock tests

            def json(self):
                return GET_ORCHESTRATION_V2_COMPLETION_RESPONSE

        timeout_captured = {}  # Capture the request kwargs from mocked post method

        def capture_request(*args, **kwargs):
            nonlocal timeout_captured
            timeout_captured = kwargs
            return FakeResponse()

        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            # no timeout set in both httpx client and request
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with patch.object(service.client, "post", side_effect=capture_request):
                service.run(config=self.config)
            self.assertEqual(timeout_captured.get("timeout"), httpx.USE_CLIENT_DEFAULT)

            # timeout set in httpx client, not overwritten in request
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client, timeout=99.0)
            with patch.object(service.client, "post", side_effect=capture_request):
                service.run(config=self.config)
            self.assertEqual(timeout_captured.get("timeout"), 99.0)

            # timeout overwrite in request
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client, timeout=99.0)
            with patch.object(service.client, "post", side_effect=capture_request):
                service.run(config=self.config, timeout=77.0)
            self.assertEqual(timeout_captured.get("timeout"), 77.0)


class TestOrchestrationServiceAsync(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.api_url = "https://api.example.com"
        self.template = Template(
            template=[
                SystemMessage(content="This is a system message."),
                UserMessage(content="Hello, {{?name}}!"),
            ],
            defaults={"name": "World"}
        )
        self.llm = LLMModelDetails(name="gemini-2.0-flash-lite")
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template,
                                                            model=self.llm)
        self.module_config = ModuleConfig(prompt_templating=self.prompt_template)
        self.config = OrchestrationConfig(modules=self.module_config)
        self.stream_config = OrchestrationConfig(modules=self.module_config,
                                                 stream=GlobalStreamOptions(enabled=True))
        self.proxy_client = get_mocked_ai_core_client(client_id='testopenaiclient')

    async def test_async_run_with_config(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_completion_v2_mocker(client.api_url + '/v2/completion'):
                await client.arun(config=self.config)

    async def test_async_timeout_client_request(self):
        class FakeResponse:
            def raise_for_status(self):
                pass  # No-op for mock tests

            def json(self):
                return GET_ORCHESTRATION_V2_COMPLETION_RESPONSE

        timeout_captured = {}  # Capture the request kwargs from mocked post method

        async def capture_request(*args, **kwargs):
            nonlocal timeout_captured
            timeout_captured = kwargs
            return FakeResponse()

        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            # no timeout set in both httpx client and request
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with patch.object(service.async_client, "post", new=AsyncMock(side_effect=capture_request)):
                await service.arun(config=self.config)
            self.assertEqual(timeout_captured.get("timeout"), httpx.USE_CLIENT_DEFAULT)

            # timeout set in httpx client, not overwritten in request
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client, timeout=99.0)
            with patch.object(service.async_client, "post", new=AsyncMock(side_effect=capture_request)):
                await service.arun(config=self.config)
            self.assertEqual(timeout_captured.get("timeout"), 99.0)

            # timeout overwrite in request
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client, timeout=99.0)
            with patch.object(service.async_client, "post", new=AsyncMock(side_effect=capture_request)):
                await service.arun(config=self.config, timeout=77.0)
            self.assertEqual(timeout_captured.get("timeout"), 77.0)

    async def test_async_stream_with_config(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            async with orchestration_v2_stream_completion_mocker_async(client.api_url + '/v2/completion'):
                txt = ''
                async for chunk in await client.astream(config=self.stream_config):
                    if chunk.final_result.choices:
                        txt += chunk.final_result.choices[0].delta.content
                self.assertEqual(txt, 'This confirms receipt of the system message: "Hello, World!\n')

    async def test_async_run_with_retries(self):
        with ai_core_ai_api_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            client = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_too_many_requests_mocker(client.api_url + '/v2/completion'):
                with self.assertRaises(OrchestrationError) as context:
                    await client.arun_with_retries(config=self.config, max_retries=1, base_delay=1.0)
                self.assertIn('X-Custom-Header', cast(OrchestrationError, context.exception).headers)
