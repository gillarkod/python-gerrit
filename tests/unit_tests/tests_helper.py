"""
Unit tests for gerrit.helper.process_endpoint
"""
from gerrit.helper import process_endpoint
from tests import GerritUnitTest


class TestProcessEndpoint(GerritUnitTest):
    """
    Unit tests for endpoint processing
    """
    def test_str(self):
        """
        Test that a str endpoint is returned as is
        """
        endpoint = '/a/changes/{}'.format(self.FULL_ID)
        self.assertEqual(
            process_endpoint(endpoint),
            endpoint,
        )

    def test_dict(self):
        """
        Test that a dict endpoint is returned as an encoded str
        """
        endpoint = {
            'pre': '/a/changes/',
            'data': '{}/{}'.format(
                self.PARENT,
                self.FULL_ID,
            ),
        }
        self.assertEqual(
            process_endpoint(endpoint),
            '/a/changes/{}%2F{}/'.format(
                self.PARENT,
                self.FULL_ID_QUOTED,
            ),
        )

    def test_dict_with_post(self):
        """
        Test that a dict with post endpoint is returned as an encoded str
        """
        endpoint = {
            'pre': '/a/changes/',
            'data': '{}/{}'.format(
                self.PARENT,
                self.FULL_ID,
            ),
            'post': '/submit/',
        }
        self.assertEqual(
            process_endpoint(endpoint),
            '/a/changes/{}%2F{}/submit/'.format(
                self.PARENT,
                self.FULL_ID_QUOTED,
            ),
        )

    def test_empty_dict(self):
        """
        Test that an empty dict raises
        """
        with self.assertRaises(KeyError):
            process_endpoint({})

    def test_dict_with_only_pre(self):
        """
        Test that a dict with only pre raises
        """
        with self.assertRaises(KeyError):
            process_endpoint({'pre': '/a/changes/'})

    def test_dict_with_only_data(self):
        """
        Test that a dict with only data raises
        """
        with self.assertRaises(KeyError):
            process_endpoint({'data': '{}/{}'.format(
                self.PARENT,
                self.FULL_ID,
            )})

    def test_dict_with_only_post(self):
        """
        Test that a dict with only post raises
        """
        with self.assertRaises(KeyError):
            process_endpoint({'post': '/submit/'})
