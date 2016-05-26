"""
Connection
==========

Set up connection to gerrit
"""

import requests
from requests.auth import HTTPBasicAuth
from requests.utils import get_netrc_auth

from Gerrit.error import GerritError


class Connection(object):
    """Set up connection to gerrit"""

    def __init__(self, url, auth_id=None, auth_pw=None, debug=True):
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
                raise GerritError.CredentialsNotFound("No Credentials for %s found in .netrc" % self._url)

            auth_id, auth_pw = netrc_auth

        if auth_id is None or auth_pw is None:
            raise GerritError.CredentialsNotFound("Partial credenials given.")
        # We got everything as we expected, create the HTTPBasicAuth object.
        self._auth = HTTPBasicAuth(auth_id, auth_pw)

    def call(self, request='get', r_endpoint=None, r_payload=None, ):
        """
        Send request to gerrit.

        request needs to be either get, post or delete

        Returns a requests Response object
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
        """Get debug status"""

        return self._debug
