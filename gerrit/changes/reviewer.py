"""
Reviewer
======

Manage gerrit reviewers for a specific change_id
"""

from gerrit.error import (
    UnhandledError,
    AlreadyExists,
    AuthorizationError,
)
from gerrit.helper import decode_json


class Reviewer(object):
    """Manage gerrit reviewers for a change"""

    def __init__(self, gerrit_con, change_id):
        """
        :param gerrit_con: The connection object to gerrit
        :type gerrit_con: gerrit.Connection
        :param change_id: The Change Request ID
        :type change_id: str
        """
        self._change_id = change_id
        self._gerrit_con = gerrit_con

    def add_reviewer(self, account_id):
        """
        Endpoint for adding a reviewer to a change-id
        :param account_id: The user account that should be added as a reviewer
        :type account_id: str
        :return: You get a True boolean type if the addition of this user was successful
        :rtype: bool
        :except: LookupError, AlreadyExists, UnhandledError
        """
        r_endpoint = "/a/changes/%s/reviewers" % self._change_id
        payload = {"reviewer": "%s" % account_id}

        req = self._gerrit_con.call(
            request='post',
            r_endpoint=r_endpoint,
            r_payload=payload
        )

        result = req.content.decode('utf-8')

        if "does not identify a registered user or group" in result:
            raise LookupError(result)

        # If the above doesn't match then it should be json data we get.
        json_result = decode_json(result)

        try:
            if len(json_result.get('reviewers', False)) == 0:
                raise AlreadyExists('The requested user \'%s\' is \
                    already an reviewer' % account_id)
            elif len(json_result.get('reviewers', False)) >= 1:
                return True
        except TypeError:
            raise UnhandledError(json_result)

    def delete_reviewer(self, account_id):
        """
        Endpoint to delete a reviewer from a change-id
        :param account_id: Remove a user with account-id as reviewer.
        :type account_id: str
        :rtype: bool
        :exception: error.AuthorizationError
        """
        r_endpoint = "/a/changes/%s/reviewers/%s" % (self._change_id, account_id)

        req = self._gerrit_con.call(
            request='delete',
            r_endpoint=r_endpoint,
            r_headers={},
        )

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if "delete not permitted" in result:
            raise AuthorizationError(result)

        if status_code == 204:
            return True

        return False

    def list_reviewers(self):
        """
        Endpoint to list reviewers for a change-id
        :returns: The reviews for the specified change-id at init
        :rtype: dict
        :exception: ValueError, UnhandledError
        """
        r_endpoint = "/a/changes/%s/reviewers/" % self._change_id

        req = self._gerrit_con.call(r_endpoint=r_endpoint)

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if status_code == 404:
            raise ValueError(result)
        elif status_code != 200:
            raise UnhandledError(result)

        json_result = decode_json(result)

        return json_result
