import time
import unittest

from gen_ai_hub.proxy.core.utils import PredictionURLs, lru_cache_extended


class TestLRUCacheDecorators(unittest.TestCase):

    def test_lru_cache_clear(self):
        @lru_cache_extended()
        def test_func(x):
            test_func.counter += 1
            return x * x

        test_func.counter = 0

        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 1)
        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 1)
        test_func.cache_clear()
        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 2)

    def test_lru_cache_extended_first_arg_self(self):
        class NotHashable:
            __hash__ = None

            def __init__(self, x):
                self.counter = 0
                self.x = x

            @lru_cache_extended(first_arg_self=True)
            def test_func(self, y):
                self.counter += 1
                return self.x * y

            @property
            @lru_cache_extended(first_arg_self=True)
            def x_prop(self):
                self.counter += 1
                return self.x

        obj = NotHashable(2)
        self.assertEqual(obj.test_func(2), 4)
        self.assertEqual(obj.counter, 1)
        self.assertEqual(obj.test_func(2), 4)
        self.assertEqual(obj.counter, 1)

        obj = NotHashable(3)
        self.assertEqual(obj.test_func(2), 6)
        self.assertEqual(obj.counter, 1)
        self.assertEqual(obj.test_func(2), 6)
        self.assertEqual(obj.counter, 1)

        x = obj.x_prop
        self.assertEqual(x, obj.x)
        self.assertEqual(obj.counter, 2)
        x = obj.x_prop
        self.assertEqual(obj.counter, 2)

    def test_lru_cache_extended_refresh(self):
        @lru_cache_extended(maxsize=2)
        def test_func(x):
            test_func.counter += 1
            return x * x

        test_func.counter = 0

        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 1)
        self.assertEqual(test_func(3), 9)
        self.assertEqual(test_func.counter, 2)
        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 2)

        # Test cache clearing
        test_func(2, _recache=True)
        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 3)

    def test_lru_cache_extended_timeout(self):
        @lru_cache_extended(timeout=1, maxsize=2)
        def test_func(x):
            test_func.counter += 1
            return x * x

        test_func.counter = 0

        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 1)
        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 1)
        time.sleep(1.1)  # Wait for the cache to expire
        self.assertEqual(test_func(2), 4)  # Should recompute
        self.assertEqual(test_func.counter, 2)

    def test_lru_cache_extended_typed(self):
        @lru_cache_extended(typed=True)
        def test_func(x):
            test_func.counter += 1
            return x * x

        test_func.counter = 0

        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 1)
        self.assertEqual(test_func(2.0), 4)
        self.assertEqual(test_func.counter, 2)
        self.assertEqual(test_func(2), 4)
        self.assertEqual(test_func.counter, 2)


class TestPredictionURLs(unittest.TestCase):

    def setUp(self):
        self.prediction_urls = PredictionURLs({'model1': '/predict1', 'model2': '/predict2'})

    def test_register_and_call(self):
        self.prediction_urls.register({'model3': '/predict3'})
        url = self.prediction_urls('model3', 'http://example.com')
        self.assertEqual(url, 'http://example.com/predict3')

    def test_call_with_fixed_suffix(self):
        url = self.prediction_urls('model1', 'http://example.com', fixed_suffix='/custom')
        self.assertEqual(url, 'http://example.com/custom')

    def test_call_with_unknown_model(self):
        url = self.prediction_urls('unknown_model', 'http://example.com')
        self.assertIsNone(url)

    def test_call_with_no_suffix(self):
        url = self.prediction_urls('model1', 'http://example.com', fixed_suffix='')
        self.assertEqual(url, 'http://example.com')


if __name__ == '__main__':
    unittest.main()
