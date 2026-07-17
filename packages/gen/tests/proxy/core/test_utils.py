import time
import unittest

from gen_ai_hub.proxy.core.utils import lru_cache_extended


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


if __name__ == '__main__':
    unittest.main()
