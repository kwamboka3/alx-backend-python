#!/usr/bin/env python3

"""
This module tests the utils.access_nested_map, utils.memoize function
"""

import unittest
from typing import Any, Dict, Mapping, Sequence
from unittest.mock import Mock, patch

from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """TesTClass for NestedAccessMap"""
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map: Mapping, path: Sequence,
                               output: Any) -> None:
        """TestCase for AccessNestedMap method"""
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, output)

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError)
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping, path:
                                         Sequence, output: Any) -> None:
        """
        TestCase for AccessNestedMap keyError
        """
        with self.assertRaises(output) as err:
            result = access_nested_map(nested_map, path)
        # self.assertEqual(str(err.exception), output)


class TestGetJson(unittest.TestCase):
    """TestClass for GetJson"""
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, url: str, payload: Dict):
        """
        TestCase for get_json method
        """
        with patch('utils.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = payload
            mock_get.return_value = mock_response
            result = get_json(url)
            mock_get.assert_called_once_with(url)
            self.assertEqual(result, payload)


class TestMemoize(unittest.TestCase):
    """
    Class for TestMemoize
    """
    def test_memoize(self):
        """
        TestCase for utils.memoize
        """
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()
        with patch.object(TestClass, 'a_method', return_value=42) as pmock:
            test_obj = TestClass()
            self.assertEqual(test_obj.a_property, 42)
            self.assertEqual(test_obj.a_property, 42)
            pmock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
