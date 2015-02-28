import time
import unittest
from crawler import util


class TestUtils(unittest.TestCase):

    def test_find_urls(self):
        text = "<i>http://google.com/something</b>" \
               " and >+https://maps.yandex.ru<a> "
        urls = util.find_urls(text)

        self.assertEqual(2, len(urls))
        self.assertIn('http://google.com/something', urls)
        self.assertIn('https://maps.yandex.ru', urls)

    def test_find_no_urls(self):
        text = "Move along... https:// Nothing to see..."
        urls = util.find_urls(text)

        self.assertEqual([], urls)

    def test_try_index(self):
        xs = [1, 2]
        self.assertEqual(1, util.try_index(xs, 0))
        self.assertEqual(2, util.try_index(xs, 1))
        self.assertIsNone(util.try_index(xs, 2))

        self.assertIsNone(util.try_index([], 100))

    def test_read_timestamp(self):
        ts = int(time.time())

        self.assertIsNotNone(util.try_read_timestamp(ts))
        self.assertIsNone(util.try_read_timestamp(ts * 1000000))

    def test_select_keys(self):
        map1 = {'a': 1, 'b': 2, 'c': 3}
        map2 = util.select_keys(map1, ['a', 'c', 'd'])
        expected = {'a': 1, 'c': 3, 'd': None}

        self.assertEqual(expected, map2)

    def test_rename_key(self):
        map1 = {'a': 1024, 'b': 2, 'c': 3}
        util.rename_key(map1, 'a', 'x')

        self.assertIn('x', map1.keys())
        self.assertEqual(1024, map1['x'])

    def test_remove_key(self):
        map1 = {'a': 1024, 'b': 2, 'c': 3}
        util.remove_key(map1, 'c')

        self.assertNotIn('c', map1)
