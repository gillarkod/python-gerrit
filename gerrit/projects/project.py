"""
Project
=======

Manage gerrit projects
"""

from gerrit.helper import decode_json
from gerrit.error import UnhandledError


class Project(object):
    """Manage gerrit reviews"""

    def __init__(self, gerrit_con, name):
        """
        :param gerrit_con: The connection object to gerrit
        :type gerrit_con: gerrit.Connection
        :param name: Project name
        :type name: str
        """

        if name == '':
            raise KeyError('Project name required')

        # HTTP REST API HEADERS
        self._name = name
        self._gerrit_con = gerrit_con

        project_info = self._get_project()
        self.name = project_info.get('name')
        self.parent = project_info.get('parent')
        self.description = project_info.get('description')
        self.state = project_info.get('state')
        self.branches = project_info.get('branches')
        self.web_links = project_info.get('web_links')

    def _get_project(self):
        """
        Get ProjectInfo for a project
        :returns: Dict of the ProjectInfo for the project
        :rtype: dict
        :exception: ValueError, UnhandledError
        """
        r_endpoint = "/a/projects/%s/" % self._name

        req = self._gerrit_con.call(r_endpoint=r_endpoint)

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if status_code == 200:
            return decode_json(result)
        elif status_code == 404:
            raise ValueError(result)
        else:
            raise UnhandledError(result)
