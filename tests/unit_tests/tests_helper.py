#!/usr/bin/env python

import unittest
from gerrit.helper import process_endpoint

class TestProcessEndpoint(unittest.TestCase):
    def test_str_returns_input(self):
        endpoint = '/a/changes/project~master~I12345'
        self.assertEqual(
            process_endpoint(endpoint),
            endpoint,
        )

    def test_dict_returns_http_encoded_str(self):
        endpoint = {
            'pre': '/a/changes/',
            'data': 'parent/project~master~I12345',
        }
        self.assertEqual(
            process_endpoint(endpoint),
            '/a/changes/parent%2Fproject%7Emaster%7EI12345/',
        )

    def test_dict_with_post_returns_http_encoded_str(self):
        endpoint = {
            'pre': '/a/changes/',
            'data': 'parent/project~master~I12345',
            'post': '/submit/',
        }
        self.assertEqual(
            process_endpoint(endpoint),
            '/a/changes/parent%2Fproject%7Emaster%7EI12345/submit/',
        )

    def test_empty_dict_raises(self):
        with self.assertRaises(KeyError):
            process_endpoint({})

    def test_dict_with_only_pre_raises(self):
        with self.assertRaises(KeyError):
            process_endpoint({'pre': '/a/changes/'})

    def test_dict_with_only_data_raises(self):
        with self.assertRaises(KeyError):
            process_endpoint({'data': 'parent/project~master~I12345'})

    def test_dict_with_only_post_raises(self):
        with self.assertRaises(KeyError):
            process_endpoint({'post': '/submit/'})


def main():
    unittest.main()


if __name__ == '__main__':
    main()
