"""
Unit tests for gerrit.changes.change
"""
import mock
from gerrit.error import UnhandledError
from gerrit.changes.change import Change
from gerrit.projects.project import Project
from tests import GerritUnitTest


class ChangeTestCase(GerritUnitTest):
    """
    Unit tests for gerrit.changes.change
    """
    def setUp(self):
        self.req = mock.Mock()
        self.req.status_code = 200
        self.req.content = self.build_response({})
        self.gerrit_con = mock.Mock()
        self.gerrit_con.call.return_value = self.req

        self.req_project = mock.Mock()
        self.req_project.status_code = 200
        self.req_project.content = self.build_response({"name": "gerritproject"})
        self.gerrit_con_project = mock.Mock()
        self.gerrit_con_project.call.return_value = self.req_project

        self.req.content = self.build_response(
            {
                "id": self.FULL_ID,
                "project": self.PROJECT,
                "branch": self.BRANCH,
                "change_id": self.CHANGE_ID,
                "subject": self.SUBJECT,
                "status": self.STATUS,
                "created": self.CREATED,
                "updated": self.UPDATED,
                "mergable": self.MERGABLE,
                "insertions": self.INSERTIONS,
                "deletions": self.DELETIONS,
                "number": self.NUMBER,
                "owner": self.OWNER,
            }
        )
        self.change = Change(self.gerrit_con).get_change(
            self.PROJECT,
            self.BRANCH,
            self.CHANGE_ID,
        )

    def test_get_change_returns_change(self):
        """
        Test that a change is properly parsed
        """
        self.assertEqual(self.change.full_id, self.FULL_ID)
        self.assertEqual(self.change.project, self.PROJECT)
        self.assertEqual(self.change.branch, self.BRANCH)
        self.assertEqual(self.change.change_id, self.CHANGE_ID)
        self.assertEqual(self.change.subject, self.SUBJECT)
        self.assertEqual(self.change.status, self.STATUS)
        self.assertEqual(self.change.created, self.CREATED)
        self.assertEqual(self.change.updated, self.UPDATED)
        self.assertEqual(self.change.mergable, self.MERGABLE)
        self.assertEqual(self.change.insertions, self.INSERTIONS)
        self.assertEqual(self.change.deletions, self.DELETIONS)
        self.assertEqual(self.change.number, self.NUMBER)
        self.assertEqual(self.change.owner, self.OWNER)

    def test_get_change_project_object(self):
        """
        Test that a change can be fetched when using a project object
        """
        project = Project(self.gerrit_con).get_project(self.PROJECT)
        change = Change(self.gerrit_con).get_change(
            project,
            self.BRANCH,
            self.CHANGE_ID
        )
        self.assertEqual(change.full_id, self.FULL_ID)

    def test_get_change_empty_project(self):
        """
        Test that fetching a change with an empty project raises an error
        """
        with self.assertRaises(KeyError):
            Change(self.gerrit_con).get_change(
                '',
                self.BRANCH,
                self.CHANGE_ID
            )

    def test_get_change_empty_branch(self):
        """
        Test that fetching a change with an empty branch raises an error
        """
        with self.assertRaises(KeyError):
            Change(self.gerrit_con).get_change(
                self.PROJECT,
                '',
                self.CHANGE_ID
            )

    def test_get_change_empty_change_id(self):
        """
        Test that fetching a change with an empty change ID raises an error
        """
        with self.assertRaises(KeyError):
            Change(self.gerrit_con).get_change(
                self.PROJECT,
                self.BRANCH,
                ''
            )

    def test_get_change_doesnt_exist(self):
        """
        Test that fetching a change that doesn't exist raises an error
        """
        self.req.status_code = 404

        with self.assertRaises(ValueError):
            Change(self.gerrit_con).get_change(
                self.PROJECT,
                self.BRANCH,
                self.CHANGE_ID
            )

    def test_get_change_unhandled_error(self):
        """
        Test that an unhandled error from gerrit raises an error
        """
        self.req.status_code = 503

        with self.assertRaises(UnhandledError):
            Change(self.gerrit_con).get_change(
                self.PROJECT,
                self.BRANCH,
                self.CHANGE_ID
            )

    def test_create_change_success(self):
        """
        Test that a change is successfully created
        """
        self.req.status_code = 201

        with mock.patch.object(Change, 'get_change') as mock_get_change:
            Change(self.gerrit_con).create_change(
                self.PROJECT,
                self.SUBJECT,
                self.BRANCH,
                {'status': 'DRAFT'},
            )
            mock_get_change.assert_called_with(
                self.PROJECT,
                self.BRANCH,
                self.CHANGE_ID,
            )

    def test_create_change_fail(self):
        """
        Test that failing to create a change raises an error
        """
        self.req.status_code = 404

        with self.assertRaises(UnhandledError):
            Change(self.gerrit_con).create_change(
                self.PROJECT,
                self.SUBJECT,
                self.BRANCH,
                {'status': 'DRAFT'}
            )

    def test_create_change_project_obj(self):
        """
        Test that a change is successfully created when using a project object
        """
        self.req.status_code = 201

        with mock.patch.object(Change, 'get_change') as mock_get_change:
            project = Project(self.gerrit_con_project).get_project(self.PROJECT)
            Change(self.gerrit_con).create_change(
                project,
                self.SUBJECT,
                self.BRANCH,
                {'status': 'DRAFT'}
            )
            mock_get_change.assert_called_with(
                self.PROJECT,
                self.BRANCH,
                self.CHANGE_ID,
            )

    def test_submit_change_success(self):
        """
        Test that submitting a change is successful
        """
        self.req.content = self.build_response({"status": "MERGED"})
        self.change.submit_change()
        self.gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint={
                'pre': '/a/changes/',
                'data': self.FULL_ID,
                'post': '/submit/',
            },
            r_payload={},
        )
        self.assertEqual(self.change.status, 'MERGED')

    def test_submit_change_with_options(self):
        """
        Test that a change can be submitted with options
        """
        self.req.content = self.build_response({"status": "MERGED"})
        self.change.submit_change({'NOTIFY': 'NONE'})
        self.gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint={
                'pre': '/a/changes/',
                'data': self.FULL_ID,
                'post': '/submit/',
            },
            r_payload={'NOTIFY': 'NONE'}
        )
        self.assertEqual(self.change.status, 'MERGED')

    def test_submit_change_fail(self):
        """
        Test that a submit raises an error if it is blocked
        """
        self.req.status_code = 409
        self.req.content = self.build_response('blocked by Verify')
        with self.assertRaises(UnhandledError):
            self.change.submit_change()

    def test_add_reviewer(self):
        """
        Test that a reviewer can be added
        """
        self.req.content = self.build_response({"reviewers": [self.USER]})
        self.assertTrue(self.change.add_reviewer(self.USER))
        self.gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint='/a/changes/{}/reviewers'.format(self.CHANGE_ID),
            r_payload={'reviewer': self.USER},
        )

    def test_delete_reviewer(self):
        """
        Test that a reviewer can be deleted
        """
        self.req.status_code = 204
        self.assertTrue(self.change.delete_reviewer(self.USER))
        self.gerrit_con.call.assert_called_with(
            request='delete',
            r_endpoint='/a/changes/{}/reviewers/{}'.format(self.CHANGE_ID, self.USER),
            r_headers={},
        )

    def test_list_reviewer(self):
        """
        Test that reviewers can be listed
        """
        self.change.list_reviewers()
        self.gerrit_con.call.assert_called_with(
            r_endpoint='/a/changes/{}/reviewers/'.format(self.CHANGE_ID),
        )

    def test_set_review(self):
        """
        Test that a review can be set
        """
        self.change.set_review()
        self.gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint='/a/changes/{}/revisions/current/review'.format(self.CHANGE_ID),
            r_payload={}
        )

    def test_parent_project_quote(self):
        """
        Test that a quoted id is unquoted
        """
        self.req.content = self.build_response(
            {
                "id": "{}%2F{}".format(
                    self.PARENT,
                    self.FULL_ID,
                ),
            }
        )

        change = Change(self.gerrit_con).get_change(
            '{}/{}'.format(
                self.PARENT,
                self.PROJECT,
            ),
            self.BRANCH,
            self.CHANGE_ID
        )
        self.assertEqual(
            change.full_id,
            '{}/{}'.format(
                self.PARENT,
                self.FULL_ID,
            ),
        )

    def test_parent_project_no_quote(self):
        """
        Test that an already unquoted id is not unquoted
        """
        self.req.content = self.build_response(
            {
                "id": "{}/{}".format(
                    self.PARENT,
                    self.CHANGE_ID,
                ),
            }
        )

        change = Change(self.gerrit_con).get_change(
            '{}/{}'.format(
                self.PARENT,
                self.PROJECT,
            ),
            self.BRANCH,
            self.CHANGE_ID
        )
        self.assertEqual(
            change.full_id,
            '{}/{}'.format(
                self.PARENT,
                self.CHANGE_ID,
            ),
        )
