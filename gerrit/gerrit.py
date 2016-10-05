"""
Gerrit
======

Set up connection to gerrit
"""

import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests.utils import get_netrc_auth

from gerrit.changes.revision import Revision
from gerrit.changes.change import Change
from gerrit.error import CredentialsNotFound
from gerrit.projects.project import Project
from gerrit.helper import process_endpoint


class Gerrit(object):
    """Set up connection to gerrit"""

    def __init__(self, url, auth_type=None, **kwargs):
        """
        :param url: URL to the gerrit server
        :type url: str
        :param auth_type: Authentication method preferred
        :type auth_type: str
        """

        # HTTP REST API HEADERS
        self._requests_headers = {
            'content-type': 'application/json',
        }

        self._url = url.rstrip('/')

        self._auth = None

        if auth_type:
            if auth_type == 'http':
                self._http_auth(**kwargs)
            else:
                raise NotImplementedError(
                    "Authorization type '%s' is not implemented" %
                    auth_type)
        else:
            self._http_auth(**kwargs)

    def _netrc_auth(self):
        if get_netrc_auth(self._url):
            netrc_id, netrc_pw = get_netrc_auth(self._url)
        else:
            raise CredentialsNotFound(
                "No Credentials for %s found in .netrc" %
                self._url)
        return netrc_id, netrc_pw

    def _http_auth(self, **kwargs):
        # Assume netrc file if no auth_id or auth_pw was given.
        if 'auth_id' in kwargs and 'auth_pw' in kwargs:
            auth_id = kwargs['auth_id']
            auth_pw = kwargs['auth_pw']
        elif 'auth_id' not in kwargs and 'auth_pw' not in kwargs:
            auth_id, auth_pw = self._netrc_auth()
        else:
            raise CredentialsNotFound(
                'Supply both auth_id and auth_pw or neither')

        if 'auth_method' not in kwargs:
            self._http_basic_auth(auth_id, auth_pw)
        elif kwargs['auth_method'] == 'basic':
            self._http_basic_auth(auth_id, auth_pw)
        elif kwargs['auth_method'] == 'digest':
            self._http_digest_auth(auth_id, auth_pw)
        else:
            raise NotImplementedError(
                "Authorization method '%s' for auth_type 'http' is not implemented" %
                kwargs['auth_method'])

    def _http_basic_auth(self, auth_id, auth_pw):
        # We got everything as we expected, create the HTTPBasicAuth object.
        self._auth = HTTPBasicAuth(auth_id, auth_pw)

    def _http_digest_auth(self, auth_id, auth_pw):
        # We got everything as we expected, create the HTTPDigestAuth object.
        self._auth = HTTPDigestAuth(auth_id, auth_pw)

    def call(self, request='get', r_endpoint=None, r_payload=None, r_headers=None):
        """
        Send request to gerrit.
        :param request: The type of http request to perform
        :type request: str
        :param r_endpoint: The gerrit REST API endpoint to hit
        :type r_endpoint: str
        :param r_payload: The data to send to the specified API endpoint
        :type r_payload: dict

        :return: The http request
        :rtype: requests.packages.urllib3.response.HTTPResponse
        """

        if r_headers is None:
            r_headers = self._requests_headers

        request_do = {
            'get': requests.get,
            'put': requests.put,
            'post': requests.post,
            'delete': requests.delete
        }
        req = request_do[request](
            url=self._url + process_endpoint(r_endpoint),
            auth=self._auth,
            headers=r_headers,
            json=r_payload
        )
        return req

    def get_revision(self, change_id, revision_id=None):
        """
        Get a revision
        :param change_id: The Change-Id to fetch from gerrit
        :type change_id: str
        :param revision_id: The optional patch set for the change
        :type revision_id: str

        :return: Review object
        :rtype: gerrit.changes.Revision
        """

        return Revision(self, change_id, revision_id)

    def create_project(self, name, options=None):
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

        project = Project(self)
        return project.create_project(name, options)

    def get_project(self, name):
        """
        Get a project
        :param name: Project name to get
        :type name: str

        :return: Project object
        :rtype: gerrit.projects.Project
        """

        project = Project(self)
        return project.get_project(name)

    def create_change(self, project, subject, branch='master', options=None):
        """
        Create a change
	:param project: Project to create change in
	:type project: str or gerrit.project.Project
	:param subject: Subject of the change
	:type subject: str
	:param branch: The name of the target branch
	:type branch: str
	:param options: Additional options
	:type options: dict
	"""

        change = Change(self)
        return change.create_change(project, subject, branch, options)

    def get_change(self, project, change_id, branch='master'):
        """
        Get a change
        :param project: Project that contains change
        :type project: str or gerrit.projects.Project
        :param change_id: ID of change
        :type change_id: str
        :param branch: Branch change exists in
        :type branch: str
        """
        change = Change(self)
        return change.get_change(project, branch, change_id)
