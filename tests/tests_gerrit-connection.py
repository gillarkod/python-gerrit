#!/usr/bin/env python

import unittest

import mock

from gerrit.connection import Connection
from gerrit.error import (
    CredentialsNotFound,
)


class GerritConTestCase(unittest.TestCase):
    @mock.patch('gerrit.connection.get_netrc_auth')
    def test_init_with_netrc(self, mock_get_netrc_auth):
        # Set up mock
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')

        # Instantiate gerrit Con
        reference = Connection(url='http://domain.com')

        # Make sure get_netrc_auth is called since we have no specified the credentials
        self.assertTrue(mock_get_netrc_auth.called,
                        'Failed to call get_netrc_auth if credentials were not specified.')

        # Check that the _auth HTTPBasicAuth object contains the
        # given credentials

        self.assertEqual('user_found', reference._auth.username)
        self.assertEqual('password_found', reference._auth.password)

    @mock.patch('gerrit.connection.get_netrc_auth')
    def test_init_credentials_given(self, mock_get_netrc_auth):
        # Instantiate gerrit Con
        reference = Connection(url='http://domain.com',
                               auth_id='user_given',
                               auth_pw='password_given')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertFalse(
            mock_get_netrc_auth.called,
            'Failed to not call get_netrc_auth if credentials were given.'
        )

        # Check that the _auth HTTPBasicAuth object contains the
        # given credentials

        self.assertEqual('user_given', reference._auth.username)
        self.assertEqual('password_given', reference._auth.password)

    @mock.patch('gerrit.connection.get_netrc_auth')
    def test_init_credentials_not_found(self, mock_get_netrc_auth):
        # Set up mock
        mock_get_netrc_auth.return_value = False

        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            reference = Connection(url='http://domain.com')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertTrue(mock_get_netrc_auth.called,
                        'Failed to call get_netrc_auth if credentials were not given.')

    @mock.patch('gerrit.connection.get_netrc_auth')
    def test_init_partialAuth_id_given(self, mock_get_netrc_auth):
        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            reference = Connection(url='http://domain.com',
                                   auth_id='user_given')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertFalse(mock_get_netrc_auth.called,
                         'Failed to not call get_netrc_auth if credentials were given.')

    @mock.patch('gerrit.connection.get_netrc_auth')
    def test_init_partialAuth_pw_given(self, mock_get_netrc_auth):
        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            reference = Connection(url='http://domain.com',
                                   auth_pw='pass_given')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertFalse(mock_get_netrc_auth.called,
                         'Failed to not call get_netrc_auth if credentials were given.')


class GerritError(unittest.TestCase):
    """Tests for gerrit/error.py"""

    def test_exception_has_message(self):
        """Exceptions should have messages"""

        with self.assertRaises(CredentialsNotFound) as cm:
            raise CredentialsNotFound("Test message")
        self.assertEqual("Test message", str(cm.exception))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
