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

    def __init__(self, url, auth_id=None, auth_pw=None, debug=True):
        """
        :param url: URL to the gerrit server
        :type url: str
        :param auth_id: Username to authenticate with
        :type auth_id: str
        :param auth_pw: Password for username to authenticate with
        :type auth_pw: str
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

        # Assume netrc file if no auth_id or auth_pw was given.
        if auth_id is None and auth_pw is None:
            netrc_auth = get_netrc_auth(self._url)
            if not netrc_auth:
                raise CredentialsNotFound(
                    "No Credentials for %s found in .netrc" %
                    self._url)

            auth_id, auth_pw = netrc_auth

        if auth_id is None or auth_pw is None:
            raise CredentialsNotFound("Partial credentials given.")
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
