"""
Unit tests for gerrit.changes.change
"""
import unittest
import mock
from gerrit.error import CredentialsNotFound
from gerrit.gerrit import (
    Gerrit,
    HTTPDigestAuth,
    HTTPBasicAuth,
)
from gerrit.projects.project import Project
from gerrit.changes.revision import Revision
from gerrit.changes.change import Change
from tests import GerritUnitTest


class GerritTestCase(GerritUnitTest):
    """
    Basic class with standard settings and mocks
    """
    def setUp(self):
        self.mock_http_basic_auth = mock.patch('gerrit.gerrit.HTTPBasicAuth').start()
        self.mock_http_basic_auth.side_effect = HTTPBasicAuth
        self.mock_http_digest_auth = mock.patch('gerrit.gerrit.HTTPDigestAuth').start()
        self.mock_http_digest_auth.side_effect = HTTPDigestAuth
        self.mock_get_netrc_auth = mock.patch('gerrit.gerrit.get_netrc_auth').start()
        self.mock_get_netrc_auth.return_value = (self.USERNAME, self.PASSWORD)


class GerritInitTestCase(GerritTestCase):
    """
    Unit tests for initiating a Gerrit connection
    """
    def auth_ok(self, reference, auth_mock=None):
        """
        Helper method for testing if authentication was done correctly
        """
        # pylint: disable=protected-access
        self.assertEqual(
            reference._auth.username,
            self.USERNAME,
        )
        self.assertEqual(
            reference._auth.password,
            self.PASSWORD,
        )
        if auth_mock is not None:
            auth_mock.assert_called_once_with(self.USERNAME, self.PASSWORD)

    def test_no_parameters(self):
        """
        Init without any auth parameters
        """
        reference = Gerrit(
            url=self.URL,
        )

        self.auth_ok(reference, self.mock_http_basic_auth)

    def test_type_http(self):
        """
        Init with auth_type parameter set to 'http'
        """
        reference = Gerrit(
            url=self.URL,
            auth_type='http',
        )

        self.auth_ok(reference, self.mock_http_basic_auth)

    def test_type_http_method_basic(self):
        """
        Init with auth_type parameter set to 'http' and auth_method set to 'basic'
        """
        reference = Gerrit(
            url=self.URL,
            auth_type='http',
            auth_method='basic',
        )

        self.auth_ok(reference, self.mock_http_basic_auth)

    def test_type_http_method_digest(self):
        """
        Init with auth_type parameter set to 'http' and auth_method set to 'digest'
        """
        reference = Gerrit(
            url=self.URL,
            auth_type='http',
            auth_method='digest',
        )

        self.auth_ok(reference, self.mock_http_digest_auth)

    def test_invalid_type(self):
        """
        Init with invalid auth_type 'invalid'
        """
        with self.assertRaises(NotImplementedError) as err:
            Gerrit(url=self.URL, auth_type='invalid')
        self.assertEqual("Authorization type 'invalid' is not implemented", str(err.exception))

    def test_invalid_method(self):
        """
        Init with invalid auth_method 'invalid'
        """
        with self.assertRaises(NotImplementedError) as err:
            Gerrit(url=self.URL, auth_method='invalid')
        self.assertEqual(
            "Authorization method 'invalid' for auth_type 'http' is not implemented",
            str(err.exception),
        )

    def test_netrc(self):
        """
        Test that netrc is used if no credentials are specified
        """
        # Instantiate gerrit Con
        reference = Gerrit(url=self.URL)

        # Make sure get_netrc_auth is called since we have no specified the credentials
        self.mock_get_netrc_auth.assert_called_with(self.URL)

        # Check that the _auth HTTPBasicAuth object contains the
        # given credentials
        self.auth_ok(reference)

    def test_credentials(self):
        """
        Test that netrc is not used when credentials are specified
        """
        # Instantiate gerrit Con
        reference = Gerrit(
            url=self.URL,
            auth_id=self.USERNAME,
            auth_pw=self.PASSWORD,
        )

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.mock_get_netrc_auth.assert_not_called()

        # Check that the _auth HTTPBasicAuth object contains the
        # given credentials
        self.auth_ok(reference)

    def test_credentials_not_found(self):
        """
        Test that is raises if netrc credentials can not be found
        """
        # Set up mock
        self.mock_get_netrc_auth.return_value = False

        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            Gerrit(
                url=self.URL,
            )

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.mock_get_netrc_auth.assert_called_once_with(self.URL)

    def test_partial_id_given(self):
        """
        Test that it raises if only username is specified
        """
        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            Gerrit(
                url=self.URL,
                auth_id=self.USERNAME,
            )

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.mock_get_netrc_auth.assert_not_called()

    def test_partial_pw_given(self):
        """
        Test that it raises if only password is specified
        """
        # Instantiate gerrit Con
        with self.assertRaises(CredentialsNotFound):
            Gerrit(
                url=self.URL,
                auth_pw=self.PASSWORD,
            )

        # Make sure get_netrc_auth is not called since we have given the credentials.
        self.mock_get_netrc_auth.assert_not_called()


class GerritRevisionTestCase(GerritTestCase):
    """
    Unit tests for getting a revision
    """
    def test_get_revision(self):
        """
        Test that a revision can be fetched
        """
        reference = Gerrit(url=self.URL)
        revision = reference.get_revision('my-revision')
        self.assertIsInstance(revision, Revision)


class GerritProjectTestCase(GerritTestCase):
    """
    Unit tests for projects
    """
    def setUp(self):
        super().setUp()
        self.req = mock.Mock()
        self.req.status_code = 200
        self.req.content = self.build_response({})
        self.call = mock.Mock()
        self.call.return_value = self.req

    def test_create_project(self):
        """
        Test that a project can be created
        """
        self.req.status_code = 201
        reference = Gerrit(url=self.URL)
        reference.call = self.call
        with mock.patch.object(Project, 'get_project'):
            reference.create_project(self.PROJECT)
            self.call.assert_called_with(
                request='put',
                r_endpoint='/a/projects/{}'.format(self.PROJECT),
                r_payload={},
            )

    def test_get_project(self):
        """
        Test that a project can be fetched
        """
        reference = Gerrit(url=self.URL)
        reference.call = self.call
        reference.get_project(self.PROJECT)
        self.call.assert_called_with(
            r_endpoint='/a/projects/{}/'.format(self.PROJECT),
        )


class GerritChangeTestCase(GerritTestCase):
    """
    Unit tests for changes
    """
    def setUp(self):
        super().setUp()
        self.mock_post = mock.patch('gerrit.gerrit.requests.post').start()
        self.post = mock.Mock()
        self.post.status_code = 201
        self.post.content = self.build_response(
            {
                "change_id": self.CHANGE_ID,
            }
        )
        self.mock_post.return_value = self.post

        self.mock_get = mock.patch('gerrit.gerrit.requests.get').start()
        self.get = mock.Mock()
        self.get.status_code = 200
        self.get.content = self.build_response({})
        self.mock_get.return_value = self.get

    def test_create_change(self):
        """
        Test that a change can be created
        """
        reference = Gerrit(url=self.URL)
        change = reference.create_change(self.PROJECT, 'change status')
        self.assertIsInstance(change, Change)
        self.mock_post.assert_called_with(
            auth=mock.ANY,
            headers=mock.ANY,
            json=mock.ANY,
            url='{}/a/changes/'.format(self.URL)
        )

    def test_get_change(self):
        """
        Test that a change can be fetched
        """
        self.get.content = self.build_response(
            {
                "name": self.PROJECT,
                "parent": self.PARENT,
                "description": self.DESCRIPTION,
                "state": self.STATE,
            }
        )

        reference = Gerrit(url=self.URL)
        change = reference.get_change(self.PROJECT, self.CHANGE_ID)
        self.assertIsInstance(change, Change)
        self.mock_get.assert_called_with(
            auth=mock.ANY,
            headers=mock.ANY,
            json=mock.ANY,
            url='{}/a/changes/{}%7E{}%7E{}/'.format(
                self.URL,
                self.PROJECT,
                self.BRANCH,
                self.CHANGE_ID,
            )
        )


class GerritError(unittest.TestCase):
    """
    Unit tests for errors
    """

    def test_exception_has_message(self):
        """
        Exceptions should have messages
        """
        with self.assertRaises(CredentialsNotFound) as err:
            raise CredentialsNotFound("Test message")
        self.assertEqual("Test message", str(err.exception))
