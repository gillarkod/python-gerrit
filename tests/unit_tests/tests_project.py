"""
Unit tests for gerrit.projects.project
"""
from copy import copy
import mock
from gerrit.error import (
    UnhandledError,
    AlreadyExists,
)
from gerrit.projects.project import Project
from tests import GerritUnitTest


class ProjectTestCase(GerritUnitTest):
    """
    Unit tests for handling projects
    """
    def setUp(self):
        self.project_content = self.build_response(
            {
                'name': self.PROJECT,
                'parent': self.PARENT,
                'description': self.DESCRIPTION,
                'state': self.STATE,
            }
        )
        self.gerrit_con = mock.Mock()
        self.req = mock.Mock()
        self.req.status_code = 200
        self.req.content = self.build_response({})
        self.gerrit_con.call.return_value = self.req
        self.req_delete = copy(self.req)
        self.req_delete.status_code = 204

    def test_create(self):
        """
        Test that a project can be created
        """
        self.req.status_code = 201
        with mock.patch.object(Project, 'get_project') as mock_get_project:
            project = Project(self.gerrit_con)
            project.create_project(
                self.PROJECT,
                {'description': self.DESCRIPTION},
            )
            self.gerrit_con.call.assert_called_with(
                request='put',
                r_payload={'description': self.DESCRIPTION},
                r_endpoint='/a/projects/{}'.format(self.PROJECT),
            )
            mock_get_project.assert_called_with(self.PROJECT)

    def test_create_without_options(self):
        """
        Test that a project can be created without options
        """
        self.req.status_code = 201
        with mock.patch.object(Project, 'get_project') as mock_get_project:
            project = Project(self.gerrit_con)
            project.create_project(
                self.PROJECT,
                None,
            )
            self.gerrit_con.call.assert_called_with(
                request='put',
                r_payload={},
                r_endpoint='/a/projects/{}'.format(self.PROJECT),
            )
            mock_get_project.assert_called_with(self.PROJECT)

    def test_create_exists(self):
        """
        Test that it raises if you try to create a project that already exists
        """
        self.req.status_code = 409
        with self.assertRaises(AlreadyExists):
            project = Project(self.gerrit_con)
            project.create_project(self.PROJECT, None)

    def test_create_unknown_error(self):
        """
        Test that it raises if server returns unknown status code
        """
        self.req.status_code = 503

        with self.assertRaises(UnhandledError):
            project = Project(self.gerrit_con)
            project.create_project(self.PROJECT, None)

    def test_get_returns_project(self):
        """
        Test that a project can be fetched
        """
        self.req.content = self.project_content

        project = Project(self.gerrit_con)
        project = project.get_project(self.PROJECT)
        self.assertEqual(project.name, self.PROJECT)
        self.assertEqual(project.parent, self.PARENT)
        self.assertEqual(project.description, self.DESCRIPTION)
        self.assertEqual(project.state, self.STATE)
        self.assertEqual(project.branches, None)
        self.assertEqual(project.web_links, None)

    def test_get_raises_on_empty_name(self):
        """
        Test that it raises if an empty project name is specified
        """
        with self.assertRaises(KeyError):
            project = Project(self.gerrit_con)
            project.get_project('')

    def test_get_raises_on_nonexist(self):
        """
        Test that it raises if the project doesn't exist
        """
        self.req.status_code = 404

        with self.assertRaises(ValueError):
            project = Project(self.gerrit_con)
            project.get_project(self.PROJECT)

    def test_get_raises_on_unknown(self):
        """
        Test that it raises if gerrit returns an unknown status code
        """
        self.req.status_code = 503

        with self.assertRaises(UnhandledError):
            project = Project(self.gerrit_con)
            project.get_project(self.PROJECT)

    def test_delete_success(self):
        """
        Test that it is possible to delete a project
        """
        self.req.content = self.project_content
        self.gerrit_con.call.side_effect = [self.req, self.req_delete]

        project = Project(self.gerrit_con)
        project = project.get_project(self.PROJECT)
        self.assertTrue(project.delete())
        self.gerrit_con.call.assert_called_with(
            request='delete',
            r_endpoint='/a/projects/{}'.format(self.PROJECT),
            r_headers={},
            r_payload=None,
        )

    def test_delete_success_options(self):
        """
        Test that it is possible to delete a project with options
        """
        self.req.content = self.project_content
        self.gerrit_con.call.side_effect = [self.req, self.req_delete]

        project = Project(self.gerrit_con)
        project = project.get_project(self.PROJECT)
        self.assertTrue(project.delete({'force': True}))
        self.gerrit_con.call.assert_called_with(
            request='delete',
            r_endpoint='/a/projects/{}'.format(self.PROJECT),
            r_headers={},
            r_payload={'force': True},
        )

    def test_delete_fails(self):
        """
        Test that failing to delete a project raises
        """
        self.req_delete.status_code = 400
        self.req.content = self.project_content
        self.gerrit_con.call.side_effect = [self.req, self.req_delete]

        project = Project(self.gerrit_con)
        project = project.get_project(self.PROJECT)
        with self.assertRaises(UnhandledError):
            project.delete()

    def test_project_eq(self):
        """
        Test that projects can be compared
        """
        self.req.content = self.project_content

        project = Project(self.gerrit_con)
        project1 = project.get_project(self.PROJECT)
        project2 = project.get_project(self.PROJECT)
        self.assertEqual(project1, project2)
