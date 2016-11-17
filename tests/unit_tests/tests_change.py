import unittest

import mock

from gerrit.error import UnhandledError
from gerrit.changes.change import Change
from gerrit.projects.project import Project


class ChangeTestCase(unittest.TestCase):
    def test_get_change_returns_change(self):
        req = mock.Mock()
        req.status_code = 200
        content_string = (
            ')]}\''
            '{"id": "gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2", '
            '"project": "gerritproject", '
            '"branch": "master", '
            '"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2", '
            '"subject": "My change", '
            '"status": "NEW", '
            '"created": "2013-02-01 09:59:32.126000000", '
            '"updated": "2013-02-21 11:16:36.775000000", '
            '"mergable": true, '
            '"insertions": 34, '
            '"deletions": 101, '
            '"number": 3965, '
            '"owner": {"name": "John Doe"}}'
        )
        req.content = content_string.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        self.assertEqual(change.full_id, 'gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')
        self.assertEqual(change.project, 'gerritproject')
        self.assertEqual(change.branch, 'master')
        self.assertEqual(change.change_id, 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')
        self.assertEqual(change.subject, 'My change')
        self.assertEqual(change.status, 'NEW')
        self.assertEqual(change.created, '2013-02-01 09:59:32.126000000')
        self.assertEqual(change.updated, '2013-02-21 11:16:36.775000000')
        self.assertTrue(change.mergable)
        self.assertEqual(change.insertions, 34)
        self.assertEqual(change.deletions, 101)
        self.assertEqual(change.number, 3965)
        self.assertEqual(change.owner, {'name': 'John Doe'})

    def test_get_change_project_object(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = ')]}\'{"id": "gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        pjt = Project(gerrit_con)
        project = pjt.get_project('gerritproject')
        cng = Change(gerrit_con)
        change = cng.get_change(
            project,
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        self.assertEqual(change.full_id, 'gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')

    def test_get_change_empty_project(self):
        gerrit_con = mock.Mock()
        with self.assertRaises(KeyError):
            cng = Change(gerrit_con)
            cng.get_change(
                '',
                'master',
                'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
            )

    def test_get_change_empty_branch(self):
        gerrit_con = mock.Mock()
        with self.assertRaises(KeyError):
            cng = Change(gerrit_con)
            cng.get_change(
                'gerritproject',
                '',
                'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
            )

    def test_get_change_empty_change_id(self):
        gerrit_con = mock.Mock()
        with self.assertRaises(KeyError):
            cng = Change(gerrit_con)
            cng.get_change(
                'gerritproject',
                'master',
                ''
            )

    def test_get_change_doesnt_exist(self):
        req = mock.Mock()
        req.status_code = 404
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(ValueError):
            cng = Change(gerrit_con)
            cng.get_change(
                'gerritproject',
                'master',
                'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
            )

    def test_get_change_unhandled_error(self):
        req = mock.Mock()
        req.status_code = 503
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(UnhandledError):
            cng = Change(gerrit_con)
            cng.get_change(
                'gerritproject',
                'master',
                'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
            )

    def test_create_change_success(self):
        req = mock.Mock()
        req.status_code = 201
        req.content = ')]}\'{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with mock.patch.object(Change, 'get_change') as mock_get_change:
            cng = Change(gerrit_con)
            cng.create_change(
                'gerritproject',
                'My change',
                'master',
                {'status': 'DRAFT'},
            )
            mock_get_change.assert_called_with(
                'gerritproject',
                'master',
                'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
            )

    def test_create_change_fail(self):
        req = mock.Mock()
        req.status_code = 404
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(UnhandledError):
            cng = Change(gerrit_con)
            cng.create_change(
                'gerritproject',
                'My change',
                'master',
                {'status': 'DRAFT'}
            )

    def test_create_change_project_object(self):
        req = mock.Mock()
        req.status_code = 201
        req.content = ')]}\'{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        req_project = mock.Mock()
        req_project.status_code = 200
        req_project.content = ')]}\'{"name": "gerritproject"}'.encode('utf-8')
        gerrit_con_project = mock.Mock()
        gerrit_con_project.call.return_value = req_project

        with mock.patch.object(Change, 'get_change') as mock_get_change:
            pjt = Project(gerrit_con_project)
            project = pjt.get_project('gerritproject')
            cng = Change(gerrit_con)
            change = cng.create_change(
                project,
                'My change',
                'master',
                {'status': 'DRAFT'}
            )
            mock_get_change.assert_called_with(
                'gerritproject',
                'master',
                'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
            )

    def test_submit_change_success(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = (
            ')]}\''
            '{"id": "gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        ).encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
        )
        req.content = ')]}\'{"status": "MERGED"}'.encode('utf-8')
        change.submit_change()
        gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint={
                'pre': '/a/changes/',
                'data': 'gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
                'post': '/submit/',
            },
            r_payload={}
        )
        self.assertEqual(change.status, 'MERGED')

    def test_submit_change_success_with_options(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = (
            ')]}\''
            '{"id": "gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        ).encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
        )
        req.content = ')]}\'{"status": "MERGED"}'.encode('utf-8')
        change.submit_change({'NOTIFY': 'NONE'})
        gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint={
                'pre': '/a/changes/',
                'data': 'gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
                'post': '/submit/',
            },
            r_payload={'NOTIFY': 'NONE'}
        )
        self.assertEqual(change.status, 'MERGED')

    def test_submit_change_fail(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
        )
        req.status_code = 409
        req.content = ')]}\'blocked by Verify'.encode('utf-8')
        with self.assertRaises(UnhandledError):
            change.submit_change()

    def test_add_reviewer(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = (
            ')]}\''
            '{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        ).encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        req.content = ')]}\'{"reviewers": ["my user"]}'.encode('utf-8')
        self.assertTrue(change.add_reviewer('my user'))
        gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint='/a/changes/I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2/reviewers',
            r_payload={'reviewer': 'my user'},
        )

    def test_delete_reviewer(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = (
            ')]}\''
            '{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        ).encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        req.status_code = 204
        self.assertTrue(change.delete_reviewer('my user'))
        gerrit_con.call.assert_called_with(
            request='delete',
            r_endpoint='/a/changes/I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2/reviewers/my user',
            r_headers={},
        )

    def test_list_reviewer(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = (
            ')]}\''
            '{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        ).encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        req.status_code = 200
        change.list_reviewers()
        gerrit_con.call.assert_called_with(
            r_endpoint='/a/changes/I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2/reviewers/',
        )

    def test_set_review(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = (
            ')]}\''
            '{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        ).encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        req.status_code = 200
        change.set_review()
        gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint='/a/changes/I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2/revisions/current/review',
            r_payload={}
        )

    def test_parent_project_quote(self):
        """Test that a quoted id is unquoted"""
        req = mock.Mock()
        req.status_code = 200
        content_string = (
            ')]}\''
            '{"id": "parentproject%2Fgerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        )
        req.content = content_string.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'parentproject/gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        self.assertEqual(
            change.full_id,
            'parentproject/gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
        )


    def test_parent_project_no_quote(self):
        """Test that an already unquoted id is not unquoted"""
        req = mock.Mock()
        req.status_code = 200
        content_string = (
            ')]}\''
            '{"id": "parentproject/gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'
        )
        req.content = content_string.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        cng = Change(gerrit_con)
        change = cng.get_change(
            'parentproject/gerritproject',
            'master',
            'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        )
        self.assertEqual(
            change.full_id,
            'parentproject/gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2',
        )
