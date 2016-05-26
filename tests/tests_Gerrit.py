#!/usr/bin/env python

import unittest

import mock

from Gerrit.connection import Connection
from Gerrit.error import GerritError


class GerritConTestCase(unittest.TestCase):
    @mock.patch('Gerrit.connection.get_netrc_auth')
    def test_init_with_netrc(self, mock_get_netrc_auth):
        # Set up mock
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')

        # Instantize Gerrit Con
        reference = Connection(url='http://domain.com')

        # Make sure get_netrc_auth is called since we have no specified the credentials
        self.assertTrue(mock_get_netrc_auth.called,
                        'Failed to call get_netrc_auth if credentials were not specified.')

        # Check that the _auth HTTPBasicAuth object contains the
        # given credentials

        self.assertEqual('user_found', reference._auth.username)
        self.assertEqual('password_found', reference._auth.password)

    @mock.patch('Gerrit.connection.get_netrc_auth')
    def test_init_credentials_given(self, mock_get_netrc_auth):
        # Instantize Gerrit Con
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

    @mock.patch('Gerrit.connection.get_netrc_auth')
    def test_init_credentials_not_found(self, mock_get_netrc_auth):
        # Set up mock
        mock_get_netrc_auth.return_value = False

        # Instantize Gerrit Con
        with self.assertRaises(GerritError.CredentialsNotFound):
            reference = Connection(url='http://domain.com')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertTrue(mock_get_netrc_auth.called,
                        'Failed to call get_netrc_auth if credentials were not given.')

    @mock.patch('Gerrit.connection.get_netrc_auth')
    def test_init_partialAuth_id_given(self, mock_get_netrc_auth):
        # Instantize Gerrit Con
        with self.assertRaises(GerritError.CredentialsNotFound):
            reference = Connection(url='http://domain.com',
                                   auth_id='user_given')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertFalse(mock_get_netrc_auth.called,
                         'Failed to not call get_netrc_auth if credentials were given.')

    @mock.patch('Gerrit.connection.get_netrc_auth')
    def test_init_partialAuth_pw_given(self, mock_get_netrc_auth):
        # Instantize Gerrit Con
        with self.assertRaises(GerritError.CredentialsNotFound):
            reference = Connection(url='http://domain.com',
                                   auth_pw='pass_given')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertFalse(mock_get_netrc_auth.called,
                         'Failed to not call get_netrc_auth if credentials were given.')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
