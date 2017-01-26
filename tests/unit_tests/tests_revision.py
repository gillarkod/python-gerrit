"""
Unit tests for gerrit.changes.revision
"""
import mock
from gerrit.error import UnhandledError
from gerrit.changes.revision import Revision
from tests import GerritUnitTest


class RevisionTestCase(GerritUnitTest):
    """
    Unit tests for handling revisions
    """
    def setUp(self):
        self.req = mock.Mock()
        self.req.status_code = 200
        self.gerrit_con = mock.Mock()
        self.gerrit_con.call.return_value = self.req

    def test_set_review_success(self):
        """
        Test that a review can be set
        """
        revision = Revision(
            self.gerrit_con,
            self.CHANGE_ID,
            self.REVISION_ID,
        )
        self.assertTrue(
            revision.set_review(
                labels={"Code-Review": -1},
                message='Looks good',
                comments={
                    "README.md": [
                        {
                            "line": 23,
                            "message": "[nit] trailing whitespace"
                        },
                    ],
                },
            )
        )
        self.gerrit_con.call.assert_called_with(
            r_endpoint='/a/changes/{}/revisions/{}/review'.format(
                self.CHANGE_ID,
                self.REVISION_ID,
            ),
            r_payload={
                'labels': {'Code-Review': -1},
                'message': 'Looks good',
                'comments': {
                    'README.md': [
                        {
                            'message': '[nit] trailing whitespace',
                            'line': 23
                        },
                    ],
                },
            },
            request='post',
        )

    def test_set_review_fail(self):
        """
        Test that it raises when failing to set a review
        """
        self.req.status_code = 404
        revision = Revision(
            self.gerrit_con,
            self.CHANGE_ID,
            self.REVISION_ID,
        )
        with self.assertRaises(UnhandledError):
            revision.set_review()
        self.gerrit_con.call.assert_called_with(
            r_endpoint='/a/changes/{}/revisions/{}/review'.format(
                self.CHANGE_ID,
                self.REVISION_ID,
            ),
            r_payload={},
            request='post'
        )
