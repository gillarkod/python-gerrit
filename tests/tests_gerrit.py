#!/usr/bin/env python

import unittest

import mock

from gerrit.error import (
    CredentialsNotFound,
    AlreadyExists,
    UnhandledError,
)
from gerrit.gerrit import Gerrit
from gerrit.projects.project import Project


class GerritConTestCase(unittest.TestCase):
    @mock.patch('gerrit.gerrit.HTTPBasicAuth')
    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_without_auth_parameters(self,
                                    mock_get_netrc_auth, mock_http_basic_auth):
        """Init without any auth parameters"""
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')
        auth = mock.Mock()
        auth.username, auth.password = mock_get_netrc_auth()

        reference = Gerrit(url='http://domain.com')

        mock_http_basic_auth.assert_called_with(auth.username, auth.password)

    @mock.patch('gerrit.gerrit.HTTPBasicAuth')
    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_with_auth_type_http(self,
                                      mock_get_netrc_auth, mock_http_basic_auth):
        """Init with auth_type parameter set to 'http'"""
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')
        auth = mock.Mock()
        auth.username, auth.password = mock_get_netrc_auth()

        reference = Gerrit(url='http://domain.com', auth_type='http')

        mock_http_basic_auth.assert_called_with(auth.username, auth.password)

    @mock.patch('gerrit.gerrit.HTTPBasicAuth')
    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_with_auth_type_http_auth_method_basic(self,
                                                        mock_get_netrc_auth,
                                                        mock_http_basic_auth):
        """Init with auth_type parameter set to 'http' and auth_method set to 'basic'"""
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')
        auth = mock.Mock()
        auth.username, auth.password = mock_get_netrc_auth()

        reference = Gerrit(url='http://domain.com', auth_type='http',
                               auth_method='basic')

        mock_http_basic_auth.assert_called_with(auth.username, auth.password)

    @mock.patch('gerrit.gerrit.HTTPDigestAuth')
    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_with_auth_type_http_auth_method_digest(self,
                                                         mock_get_netrc_auth,
                                                         mock_http_digest_auth):
        """Init with auth_type parameter set to 'http' and auth_method set to 'digest'"""
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')
        auth = mock.Mock()
        auth.username, auth.password = mock_get_netrc_auth()

        reference = Gerrit(url='http://domain.com', auth_type='http',
                               auth_method='digest')

        mock_http_digest_auth.assert_called_with(auth.username, auth.password)

    def test_init_with_invalid_auth_type(self):
        """Init with invalid auth_type 'invalid'"""

        with self.assertRaises(NotImplementedError) as cm:
            reference = Gerrit(url='http://domain.com', auth_type='invalid')
        self.assertEqual("Authorization type 'invalid' is not implemented",
                         str(cm.exception))

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_with_invalid_auth_method(self, mock_get_netrc_auth):
        """Init with invalid auth_method 'invalid'"""
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')
        auth = mock.Mock()
        auth.username, auth.password = mock_get_netrc_auth()

        with self.assertRaises(NotImplementedError) as cm:
            reference = Gerrit(url='http://domain.com', auth_method='invalid')
        self.assertEqual("Authorization method 'invalid' for auth_type 'http' is not implemented",
                         str(cm.exception))

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_with_netrc(self, mock_get_netrc_auth):
        # Set up mock
        mock_get_netrc_auth.return_value = ('user_found', 'password_found')

        # Instantiate gerrit Con
        reference = Gerrit(url='http://domain.com')

        # Make sure get_netrc_auth is called since we have no specified the credentials
        self.assertTrue(mock_get_netrc_auth.called,
                        'Failed to call get_netrc_auth if credentials were not specified.')

        # Check that the _auth HTTPBasicAuth object contains the
        # given credentials

        self.assertEqual('user_found', reference._auth.username)
        self.assertEqual('password_found', reference._auth.password)

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_credentials_given(self, mock_get_netrc_auth):
        # Instantiate gerrit Con
        reference = Gerrit(url='http://domain.com',
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

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_credentials_not_found(self, mock_get_netrc_auth):
        # Set up mock
        mock_get_netrc_auth.return_value = False

        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            reference = Gerrit(url='http://domain.com')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertTrue(mock_get_netrc_auth.called,
                        'Failed to call get_netrc_auth if credentials were not given.')

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_partialAuth_id_given(self, mock_get_netrc_auth):
        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            reference = Gerrit(url='http://domain.com',
                               auth_id='user_given')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertFalse(mock_get_netrc_auth.called,
                         'Failed to not call get_netrc_auth if credentials were given.')

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    def test_init_partialAuth_pw_given(self, mock_get_netrc_auth):
        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            reference = Gerrit(url='http://domain.com',
                               auth_pw='pass_given')

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.assertFalse(mock_get_netrc_auth.called,
                         'Failed to not call get_netrc_auth if credentials were given.')


class GerritProjectTestCase(unittest.TestCase):
    @mock.patch('gerrit.gerrit.get_netrc_auth')
    @mock.patch('gerrit.gerrit.requests.put')
    @mock.patch('gerrit.gerrit.requests.get')
    def test_create_project(self, mock_get, mock_put, mock_get_netrc_auth):
        mock_get_netrc_auth.return_value = ('user', 'password')
        req = mock.Mock()
        req.status_code = 201
        mock_put.return_value = req

        get = mock.Mock()
        get.status_code = 200
        get.content = ')]}\'{"name": "gerritproject", "parent": "All-Projects", "description": "My gerrit project", "state": "ACTIVE"}'.encode('utf-8')
        mock_get.return_value = get

        reference = Gerrit(url='http://domain.com')
        project = reference.create_project('gerritproject')
        self.assertIsInstance(project, Project)
        mock_put.assert_called_with(
            auth=mock.ANY,
            headers=mock.ANY,
            json=mock.ANY,
            url='http://domain.com/a/projects/gerritproject'
        )

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    @mock.patch('gerrit.gerrit.requests.put')
    def test_create_project_exists(self, mock_requests, mock_get_netrc_auth):
        mock_get_netrc_auth.return_value = ('user', 'password')
        req = mock.Mock()
        req.status_code = 409
        mock_requests.return_value = req

        reference = Gerrit(url='http://domain.com')
        with self.assertRaises(AlreadyExists):
            reference.create_project('gerritproject')

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    @mock.patch('gerrit.gerrit.requests.put')
    def test_create_project_unknown_error(self, mock_requests, mock_get_netrc_auth):
        mock_get_netrc_auth.return_value = ('user', 'password')
        req = mock.Mock()
        req.status_code = 503
        mock_requests.return_value = req

        reference = Gerrit(url='http://domain.com')
        with self.assertRaises(UnhandledError):
            reference.create_project('gerritproject')

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
