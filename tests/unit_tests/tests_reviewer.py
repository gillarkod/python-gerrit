import unittest
import mock

from gerrit.error import (
    AlreadyExists,
    UnhandledError,
    AuthorizationError,
)
from gerrit.changes.reviewer import Reviewer


class ReviewerTestCase(unittest.TestCase):
    def test_add_reviewer_user_doesnt_exist(self):
        req = mock.Mock()
        req.content = ')]}\'my user does not identify a registered user or group'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        with self.assertRaises(LookupError):
            reviewer.add_reviewer('my user')

    def test_add_reviewer_user_is_already_reviewer(self):
        req = mock.Mock()
        req.content = ')]}\'{"reviewers": []}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        with self.assertRaises(AlreadyExists):
            reviewer.add_reviewer('my user')

    def test_add_reviewer_user_added(self):
        req = mock.Mock()
        req.content = ')]}\'{"reviewers": ["my user"]}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        self.assertTrue(reviewer.add_reviewer('my user'))

    def test_add_reviewer_unhandled_error(self):
        req = mock.Mock()
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        with self.assertRaises(UnhandledError):
            reviewer.add_reviewer('my user')

    def test_delete_reviewer_unauthorized(self):
        req = mock.Mock()
        req.content = ')]}\'delete not permitted'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        with self.assertRaises(AuthorizationError):
            reviewer.delete_reviewer('my user')

    def test_delete_reviewer_success(self):
        req = mock.Mock()
        req.content = ')]}\''.encode('utf-8')
        req.status_code = 204
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        self.assertTrue(reviewer.delete_reviewer('my user'))

    def test_delete_reviewer_fail(self):
        req = mock.Mock()
        req.content = ')]}\''.encode('utf-8')
        req.status_code = 404
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        self.assertFalse(reviewer.delete_reviewer('my user'))

    def test_list_reviewers_fail(self):
        req = mock.Mock()
        req.content = ')]}\''.encode('utf-8')
        req.status_code = 404
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        with self.assertRaises(ValueError):
            reviewer.list_reviewers()

    def test_list_reviewers_unknown_error(self):
        req = mock.Mock()
        req.content = ')]}\''.encode('utf-8')
        req.status_code = 403
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        reviewer = Reviewer(gerrit_con, 'my change id')
        with self.assertRaises(UnhandledError):
            reviewer.list_reviewers()

    def test_list_reviewers_success(self):
        req = mock.Mock()
        req.content = ''')]}\'[
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
'''.encode('utf-8')
        req.status_code = 200
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req
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

        reviewer = Reviewer(gerrit_con, 'my change id')
        self.assertEqual(reviewer.list_reviewers(), expected_result)
