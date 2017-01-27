"""
Unit tests for gerrit.changes.reviewer
"""
import mock
from gerrit.error import (
    AlreadyExists,
    UnhandledError,
    AuthorizationError,
)
from gerrit.changes.reviewer import Reviewer
from tests import GerritUnitTest


class ReviewerTestCase(GerritUnitTest):
    """
    Unit tests for handling reviewers
    """
    def setUp(self):
        self.req = mock.Mock()
        self.req.content = self.build_response()
        self.gerrit_con = mock.Mock()
        self.gerrit_con.call.return_value = self.req

    def test_add_doesnt_exist(self):
        """
        Test that it raises when trying to add a user as reviewer that doesn't exist
        """
        self.req.content = self.build_response(
            'my user does not identify a registered user or group'
        )

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        with self.assertRaises(LookupError):
            reviewer.add_reviewer(self.USER)

    def test_add_already_reviewer(self):
        """
        Test that it raises when trying to add a user that is already a reviewer
        """
        self.req.content = self.build_response({"reviewers": []})

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        with self.assertRaises(AlreadyExists):
            reviewer.add_reviewer(self.USER)

    def test_add_success(self):
        """
        Test that a user can be added as a reviewer
        """
        self.req.content = self.build_response({"reviewers": [self.USER]})

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        self.assertTrue(reviewer.add_reviewer(self.USER))

    def test_add_unhandled(self):
        """
        Test that it raises if gerrit returns an unknown content
        """
        self.req.content = self.build_response({})

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        with self.assertRaises(UnhandledError):
            reviewer.add_reviewer(self.USER)

    def test_delete_unauthorized(self):
        """
        Test that it raises when deleting a reviewer is not permitted
        """
        self.req.content = self.build_response('delete not permitted')

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        with self.assertRaises(AuthorizationError):
            reviewer.delete_reviewer(self.USER)

    def test_delete_success(self):
        """
        Test that a reviewer can be deleted
        """
        self.req.status_code = 204

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        self.assertTrue(reviewer.delete_reviewer(self.USER))
        self.gerrit_con.call.assert_called_with(
            request='delete',
            r_endpoint='/a/changes/{}/reviewers/{}'.format(self.CHANGE_ID, self.USER),
            r_headers={},
        )

    def test_delete_fail(self):
        """
        Test that it returns false if removing a reviewer fails
        """
        self.req.status_code = 404

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        self.assertFalse(reviewer.delete_reviewer(self.USER))

    def test_list_fail(self):
        """
        Test that it raises if listing reviewers fails
        :return:
        """
        self.req.status_code = 404

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        with self.assertRaises(ValueError):
            reviewer.list_reviewers()

    def test_list_unknown(self):
        """
        Test that it raises if gerrit returns an unknown status code
        """
        self.req.status_code = 403

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        with self.assertRaises(UnhandledError):
            reviewer.list_reviewers()

    def test_list_success(self):
        """
        Test that listing reviewers returns the expected result
        """
        self.req.status_code = 200
        expected_result = [
            {
                "approvals": {
                    "Verified": "+1",
                    "Code-Review": "+2"
                },
                "_account_id": 1000096,
                "name": "John Doe",
                "email": "john.doe@example.com"
            },
            {
                "approvals": {
                    "Verified": " 0",
                    "Code-Review": "-1"
                },
                "_account_id": 1000097,
                "name": "Jane Roe",
                "email": "jane.roe@example.com"
            }
        ]
        self.req.content = self.build_response(expected_result)

        reviewer = Reviewer(self.gerrit_con, self.CHANGE_ID)
        self.assertEqual(reviewer.list_reviewers(), expected_result)
