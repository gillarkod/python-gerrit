import unittest

import mock

from gerrit.error import (
    UnhandledError,
    AlreadyExists,
)
from gerrit.projects.project import Project


class ProjectTestCase(unittest.TestCase):
    def test_create_project(self):
        gerrit_con = mock.Mock()
        req = mock.Mock()
        req.status_code = 201
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con.call.return_value = req

        with mock.patch.object(Project, 'get_project') as mock_get_project:
            prj = Project(gerrit_con)
            project = prj.create_project(
                'gerritproject',
                {'description': 'My descriprion'},
            )
            gerrit_con.call.assert_called_with(
                request='put',
                r_payload={'description': 'My descriprion'},
                r_endpoint='/a/projects/gerritproject',
            )
            mock_get_project.assert_called_with('gerritproject')

    def test_create_project_without_options(self):
        gerrit_con = mock.Mock()
        req = mock.Mock()
        req.status_code = 201
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con.call.return_value = req

        with mock.patch.object(Project, 'get_project') as mock_get_project:
            prj = Project(gerrit_con)
            project = prj.create_project(
                'gerritproject',
                None,
            )
            gerrit_con.call.assert_called_with(
                request='put',
                r_payload={},
                r_endpoint='/a/projects/gerritproject',
            )
            mock_get_project.assert_called_with('gerritproject')

    @mock.patch('gerrit.gerrit.requests.put')
    def test_create_project_exists(self, mock_requests):
        gerrit_con = mock.Mock()
        req = mock.Mock()
        req.status_code = 409
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con.call.return_value = req

        with self.assertRaises(AlreadyExists):
            prj = Project(gerrit_con)
            prj.create_project('gerritproject', None)

    @mock.patch('gerrit.gerrit.get_netrc_auth')
    @mock.patch('gerrit.gerrit.requests.put')
    def test_create_project_unknown_error(self, mock_requests, mock_get_netrc_auth):
        gerrit_con = mock.Mock()
        req = mock.Mock()
        req.status_code = 503
        req.content = ')]}\'{}'.encode('utf-8')
        gerrit_con.call.return_value = req

        with self.assertRaises(UnhandledError):
            prj = Project(gerrit_con)
            prj.create_project('gerritproject', None)

    def test_get_project_returns_project(self):
        req = mock.Mock()
        req.status_code = 200
        req.content = ')]}\'{"name": "gerritproject", "parent": "All-Projects", "description": "My gerrit project", "state": "ACTIVE"}'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        pjt = Project(gerrit_con)
        project = pjt.get_project('gerritproject')
        self.assertEqual(project.name, 'gerritproject')
        self.assertEqual(project.parent, 'All-Projects')
        self.assertEqual(project.description, 'My gerrit project')
        self.assertEqual(project.state, 'ACTIVE')
        self.assertEqual(project.branches, None)
        self.assertEqual(project.web_links, None)

    def test_get_project_raises_on_empty_name(self):
        gerrit_con = mock.Mock()

        with self.assertRaises(KeyError):
            pjt = Project(gerrit_con)
            pjt.get_project('')

    def test_get_project_raises_on_nonexisting_project(self):
        req = mock.Mock()
        req.status_code = 404
        req.content = 'Project not found'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(ValueError):
            pjt = Project(gerrit_con)
            pjt.get_project('gerritproject')

    def test_get_project_raises_on_unknown_error(self):
        req = mock.Mock()
        req.status_code = 503
        req.content = 'Internal server error'.encode('utf-8')
        gerrit_con = mock.Mock()
        gerrit_con.call.return_value = req

        with self.assertRaises(UnhandledError):
            pjt = Project(gerrit_con)
            pjt.get_project('gerritproject')

    def test_delete_success(self):
        get = mock.Mock()
        get.status_code = 200
        get.content = ')]}\'{"name": "gerritproject", "parent": "All-Projects", "description": "My gerrit project", "state": "ACTIVE"}'.encode('utf-8')
        delete = mock.Mock()
        delete.status_code = 204
        gerrit_con = mock.Mock()
        gerrit_con.call.side_effect = [get, delete]

        pjt = Project(gerrit_con)
        project = pjt.get_project('gerritproject')
        self.assertTrue(project.delete())

    def test_delete_fails(self):
        get = mock.Mock()
        get.status_code = 200
        get.content = ')]}\'{"name": "gerritproject", "parent": "All-Projects", "description": "My gerrit project", "state": "ACTIVE"}'.encode('utf-8')
        delete = mock.Mock()
        delete.status_code = 400
        gerrit_con = mock.Mock()
        gerrit_con.call.side_effect = [get, delete]

        pjt = Project(gerrit_con)
        project = pjt.get_project('gerritproject')
        with self.assertRaises(UnhandledError):
            project.delete()
