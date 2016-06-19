"""
Project
=======

Manage gerrit projects
"""

from gerrit.helper import decode_json
from gerrit.error import (
    UnhandledError,
    AlreadyExists,
)


class Project(object):
    """Manage gerrit reviews"""

    def __init__(self, gerrit_con):
        """
        :param gerrit_con: The connection object to gerrit
        :type gerrit_con: gerrit.Connection
        :param name: Project name
        :type name: str
        """

        # HTTP REST API HEADERS
        self._gerrit_con = gerrit_con

        self.name = None
        self.parent = None
        self.description = None
        self.state = None
        self.branches = None
        self.web_links = None

    def __eq__(self, other):
        return self.name == other.name

    def get_project(self, name):
        """
        Get ProjectInfo for a project
        :returns: Dict of the ProjectInfo for the project
        :rtype: dict
        :exception: ValueError, UnhandledError
        """

        if name == '':
            raise KeyError('Project name required')

        r_endpoint = "/a/projects/%s/" % name

        req = self._gerrit_con.call(r_endpoint=r_endpoint)

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if status_code == 200:
            project_info = decode_json(result)
            self.name = project_info.get('name')
            self.parent = project_info.get('parent')
            self.description = project_info.get('description')
            self.state = project_info.get('state')
            self.branches = project_info.get('branches')
            self.web_links = project_info.get('web_links')
            return self
        elif status_code == 404:
            raise ValueError(result)
        else:
            raise UnhandledError(result)

    def create_project(self, name, options):
        """
        Create a project
        :param name: Name of the project
        :type name: str
        :param options: Additional options
        :type options: dict

        :return: Project if successful
        :rtype: gerrit.projects.Project
        :exception: AlreadyExists, UnhandledError
        """

        r_endpoint = "/a/projects/%s" % name

        if options is None:
            options = {}

        req = self._gerrit_con.call(
            request='put',
            r_endpoint=r_endpoint,
            r_payload=options,
        )

        result = req.content.decode('utf-8')

        if req.status_code == 201:
            return self.get_project(name)
        elif req.status_code == 409:
            raise AlreadyExists(result)
        else:
            raise UnhandledError(result)


    def delete(self):
        """
        Delete the project, requires delete-project plugin
        :returns: True if delete succeeds
        :rtype: Bool
        :exception: UnhandledError
        """
        r_endpoint = '/a/projects/%s' % self.name

        req = self._gerrit_con.call(request='delete',
                                    r_endpoint=r_endpoint,
                                    r_headers={},
                                   )

        status_code = req.status_code

        if status_code == 204:
            return True
        else:
            result = req.content.decode('utf-8')
            raise UnhandledError(result)
