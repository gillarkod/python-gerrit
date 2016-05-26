import json
import sys

import requests
from requests.auth import HTTPBasicAuth
from requests.utils import get_netrc_auth


class Gerrit(object):
    def __init__(self, url, auth_id=False, auth_pw=False):
        # HTTP REST API HEADERS
        self._requests_headers = {
            'content-type': 'application/json',
        }

        self._url = url.rstrip('/')

        # Assume netrc file!
        if not auth_id and not auth_pw:
            netrc_auth = get_netrc_auth(self._url)
            if not netrc_auth:
                print("No credentials in .netrc for %s" % self._url)
                sys.exit(1)
            auth_id, auth_pw = netrc_auth
        self._auth = HTTPBasicAuth(auth_id, auth_pw)

    def call(self, request='get', r_endpoint=None, r_payload=None, ):
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

    class UnhandledError(Exception):
        def __init__(self, message):
            self._msg = message

    class PermissionError(Exception):
        def __init__(self, message):
            self._msg = message

    class AlreadyExists(Exception):
        def __init__(self, message):
            self._msg = message


class Review(object):
    def __init__(self, gerrit_con, change_id, revision_id):
        # HTTP REST API HEADERS
        self._change_id = change_id
        self._revision_id = revision_id
        self._gerrit_con = gerrit_con

    @staticmethod
    def _decode_json(gerrit_response):
        return json.loads(gerrit_response.lstrip(')]}\''))

    def set_review(self, labels=None, message='', comments=None):
        """
        Endpoint to create a review for a change_id and a specific patchset
        :param labels: stuff
        :param message: stuff
        :param comments: stuff
        """

        if not labels:
            labels = {}
        if not comments:
            comments = {}
        r_endpoint = "/a/changes/%s/revisions/%s/review" % (self._change_id, self._revision_id)
        payload = {}

        if labels:
            payload['labels'] = labels
        if message:
            payload['message'] = message
        if comments:
            payload['comments'] = comments

        req = self._gerrit_con.call(request='post',
                                    r_endpoint=r_endpoint,
                                    r_payload=payload
                                    )

        status_code = req.status_code
        if status_code == 200:
            return True
        else:
            raise Gerrit.UnhandledError(req.content)

    def add_reviewer(self, account_id):
        """
        Endpoint for adding a reviewer to a change-id
        """
        r_endpoint = "/a/changes/%s/reviewers" % self._change_id
        payload = {"reviewer": "%s" % account_id}

        req = self._gerrit_con.call(request='post',
                                    r_endpoint=r_endpoint,
                                    r_payload=payload
                                    )

        result = req.content.decode('utf-8')

        if "does not identify a registered user or group" in result:
            raise LookupError(result)

        # If the above doesn't match then it should be json data we get.
        json_result = self._decode_json(result)
        empty_response = {'reviewers': []}

        if len(json_result.get('reviewers', False)) == 0:
            raise Gerrit.AlreadyExists('The requested user \'%s\' is already an reviewer' % account_id)
        elif len(json_result.get('reviewers', False)) >= 1:
            return True
        else:
            raise Gerrit.UnhandledError(json_result)

    def remove_reviewer(self, account_id):
        """
        Endpoint to remove a reviewer from a change-id
        """
        r_endpoint = "/a/changes/%s/reviewers/%s" % (self._change_id, account_id)

        req = self._gerrit_con.call(request='delete',
                                    r_endpoint=r_endpoint
                                    )

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if "delete not permitted" in result:
            raise Gerrit.PermissionError(result)

        if status_code == 204:
            return True

        return False

    def get_reviews(self):
        """
        Endpoint to list reviewers for a change-id
        """
        r_endpoint = "/a/changes/%s/reviewers/" % self._change_id

        req = self._gerrit_con.call(r_endpoint=r_endpoint)

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if status_code == 404:
            raise ValueError(result)
        elif status_code != 200:
            raise Gerrit.UnhandledError(result)

        json_result = self._decode_json(result)

        return json_result
