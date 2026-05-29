import asyncio
import json
import threading
import unittest
from collections import Counter
from contextlib import contextmanager

import respx
from httpx import Response

from gen_ai_hub.proxy.gen_ai_hub_proxy import temporary_headers_addition
from gen_ai_hub.proxy.native.openai import AsyncOpenAI, OpenAI
from tests.mock import (
    get_mocked_ai_core_client,
    OPENAI_EMBEDDINGS_RESPONSE
)


class AsyncOpenAITests(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_client = get_mocked_ai_core_client()

    async def test_async_embedding(self):
        kwargs = {'model_name': 'gpt-4o-mini'}
        client = AsyncOpenAI(proxy_client=self.proxy_client)

        counter = Counter()

        def mock_callback(request):
            body = json.loads(request.content.decode('utf-8'))
            self.assertEqual(body['input'], request.headers['test-func'])
            counter[request.headers['test-func']] += 1
            return Response(200, json=OPENAI_EMBEDDINGS_RESPONSE)

        @contextmanager
        def mocker(deployment_url):
            with respx.mock:
                route = respx.post(deployment_url).mock(side_effect=mock_callback)
                yield route

        n_requests = 10

        async def test_f(test_value):
            with temporary_headers_addition({'test-func': test_value}):
                for _ in range(n_requests):
                    await client.embeddings.create(**{**kwargs, 'input': test_value})

        deployment = self.proxy_client.select_deployment(model_name='text-embedding-ada-002')
        with mocker(deployment.prediction_url):
            await asyncio.gather(*[test_f(str(i)) for i in range(5)])
        for key, value in counter.items():
            self.assertEqual(value, n_requests, f"Expected {key} but got {value}")


class SyncOpenAITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.proxy_client = get_mocked_ai_core_client()

    def test_sync_embedding(self):
        kwargs = {'model_name': 'gpt-4o-mini'}
        client = OpenAI(proxy_client=self.proxy_client)

        counter = Counter()

        def mock_callback(request):
            body = json.loads(request.content.decode('utf-8'))
            self.assertEqual(body['input'], request.headers['test-func'])
            counter[request.headers['test-func']] += 1
            return Response(200, json=OPENAI_EMBEDDINGS_RESPONSE)

        @contextmanager
        def mocker(deployment_url):
            with respx.mock:
                route = respx.post(deployment_url).mock(side_effect=mock_callback)
                yield route

        n_requests = 10

        def test_f(test_value):
            with temporary_headers_addition({'test-func': test_value}):
                for _ in range(n_requests):
                    client.embeddings.create(**{**kwargs, 'input': test_value})

        deployment = self.proxy_client.select_deployment(model_name='text-embedding-ada-002')
        with mocker(deployment.prediction_url):
            threads = [
                threading.Thread(target=test_f, args=(str(i),))
                for i in range(5)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        for key, value in counter.items():
            self.assertEqual(value, n_requests, f"Expected {key} but got {value}")
