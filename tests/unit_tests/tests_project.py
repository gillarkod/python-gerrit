import unittest

import mock

from gerrit.error import UnhandledError
from gerrit.projects.project import Project


class ProjectTestCase(unittest.TestCase):
    def test_init_returns_project(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = ')]}\'{"name": "gerritproject", "parent": "All-Projects", "description": "My gerrit project", "state": "ACTIVE"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        project = Project(gerrit_con, 'gerritproject')
        self.assertEqual(project.name, 'gerritproject')
        self.assertEqual(project.parent, 'All-Projects')
        self.assertEqual(project.description, 'My gerrit project')
        self.assertEqual(project.state, 'ACTIVE')
        self.assertEqual(project.branches, None)
        self.assertEqual(project.web_links, None)

    def test_init_raises_on_empty_name(self):
        gerrit_con = mock.Mock()

        with self.assertRaises(KeyError):
            project = Project(gerrit_con, '')

    def test_init_raises_on_nonexisting_project(self):
        req = mock.Mock()
        req.status_code = 404
        req.content = 'Project not found'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(ValueError):
            project = Project(gerrit_con, 'gerritproject')

    def test_init_raises_on_unknown_error(self):
        req = mock.Mock()
        req.status_code = 503
        req.content = 'Internal server error'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(UnhandledError):
            project = Project(gerrit_con, 'gerritproject')

    def test_delete_success(self):
        get = mock.Mock()
        get.status_code = 200
        get.content = ')]}\'{"name": "gerritproject", "parent": "All-Projects", "description": "My gerrit project", "state": "ACTIVE"}'.encode('utf-8')
        delete = mock.Mock()
        delete.status_code = 204
        gerrit_con = mock.Mock()
        gerrit_con.call.side_effect = [get, delete]

        project = Project(gerrit_con, 'gerritproject')
        self.assertTrue(project.delete())

    def test_delete_fails(self):
        get = mock.Mock()
        get.status_code = 200
        get.content = ')]}\'{"name": "gerritproject", "parent": "All-Projects", "description": "My gerrit project", "state": "ACTIVE"}'.encode('utf-8')
        delete = mock.Mock()
        delete.status_code = 400
        gerrit_con = mock.Mock()
        gerrit_con.call.side_effect = [get, delete]

        project = Project(gerrit_con, 'gerritproject')
        with self.assertRaises(UnhandledError):
            project.delete()
