"""
Connection
==========

Set up connection to gerrit
"""

import requests
from requests.auth import HTTPBasicAuth
from requests.utils import get_netrc_auth

from gerrit.error import (
    CredentialsNotFound,
)


class Connection(object):
    """Set up connection to gerrit"""

    def __init__(self, url, auth_type=None, debug=True, **kwargs):
        """
        :param url: URL to the gerrit server
        :type url: str
        :param auth_type: Authentication method preferred
        :type auth_type: str
        :param debug: Verbosity for the lib
        :type debug: bool
        """
        # Should we print out the messages?
        # Default is yes, but for testing we can set this to False
        self._debug = debug

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
                    "Authorization type %s not implemented" %
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
        else:
            raise NotImplementedError(
                "Authorization method %s for auth_type http unknown" %
                kwargs['auth_method'])


    def _http_basic_auth(self, auth_id, auth_pw):
        # We got everything as we expected, create the HTTPBasicAuth object.
        self._auth = HTTPBasicAuth(auth_id, auth_pw)

    def call(self, request='get', r_endpoint=None, r_payload=None, ):
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

        request_do = {
            'get': requests.get,
            'post': requests.post,
            'delete': requests.delete
        }
        req = request_do[request](url=self._url + r_endpoint,
                                  auth=self._auth,
                                  headers=self._requests_headers,
                                  json=r_payload
                                 )
        return req

    def debug(self):
        """
        Get debug status
        :return: Debug enablement status
        :rtype: bool
        """

        return self._debug
