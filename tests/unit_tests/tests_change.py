import unittest

import mock

from gerrit.error import UnhandledError
from gerrit.changes.change import (
    Change,
    add_change,
)
from gerrit.projects.project import Project


class ChangeTestCase(unittest.TestCase):
    def test_init_returns_change(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = ')]}\'{"id": "gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2", "project": "gerritproject", "branch": "master", "change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2", "subject": "My change", "status": "NEW", "created": "2013-02-01 09:59:32.126000000", "updated": "2013-02-21 11:16:36.775000000", "mergable": true, "insertions": 34, "deletions": 101, "number": 3965, "owner": {"name": "John Doe"}}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        change = Change(gerrit_con, 'gerritproject', 'master', 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')
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

    def test_init_project_object(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = ')]}\'{"id": "gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        project = Project(gerrit_con, 'gerritproject')
        change = Change(gerrit_con, project, 'master', 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')
        self.assertEqual(change.full_id, 'gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')

    def test_init_empty_project(self):
        gerrit_con = mock.Mock()
        with self.assertRaises(KeyError):
            change = Change(gerrit_con, '', 'master', 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')

    def test_init_empty_branch(self):
        gerrit_con = mock.Mock()
        with self.assertRaises(KeyError):
            change = Change(gerrit_con, 'gerritproject', '', 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')

    def test_init_empty_change_id(self):
        gerrit_con = mock.Mock()
        with self.assertRaises(KeyError):
            change = Change(gerrit_con, 'gerritproject', 'master', '')

    def test_get_change_doesnt_exist(self):
        req = mock.Mock()
        req.status_code = 404
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(ValueError):
            Change(gerrit_con, 'gerritproject', 'master', 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')

    def test_get_change_doesnt_exist(self):
        req = mock.Mock()
        req.status_code = 503
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(UnhandledError):
            Change(gerrit_con, 'gerritproject', 'master', 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2')

    def test_add_change_success(self):
        req = mock.Mock()
        req.status_code = 201
        req.content = ')]}\'{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with mock.patch.object(Change, '_get_change') as mock_get_change:
            change = add_change(gerrit_con, 'gerritproject', 'My change', 'master', {'status': 'DRAFT'})
            mock_get_change.assert_called_with()

    def test_add_change_fail(self):
        req = mock.Mock()
        req.status_code = 404
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(UnhandledError):
            add_change(gerrit_con, 'gerritproject', 'My change', 'master', {'status': 'DRAFT'})

    def test_add_change_project_object(self):
        req = mock.Mock()
        req.status_code = 201
        req.content = ')]}\'{"change_id": "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        req_project = mock.Mock()
        req_project.status_code = 200
        req_project.content = ')]}\'{}'.encode('utf-8')
        gerrit_con_project = mock.Mock()
        gerrit_con_project.call.return_value = req_project

        with mock.patch.object(Change, '_get_change') as mock_get_change:
            project = Project(gerrit_con_project, 'gerritproject')
            change = add_change(gerrit_con, project, 'My change', 'master', {'status': 'DRAFT'})
            mock_get_change.assert_called_with()
