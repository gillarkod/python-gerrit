"""
Revision
======

Manage gerrit revisions for a change id
"""

from gerrit.error import (
    UnhandledError
)


class Revision(object):
    """Manage gerrit revisions"""

    # pylint: disable=too-few-public-methods
    # More methods are on their way

    def __init__(self, gerrit_con, change_id, revision_id):
        """
        :param gerrit_con: The connection object to gerrit
        :type gerrit_con: gerrit.Connection
        :param change_id: The Change Request ID
        :type change_id: str
        :param revision_id: The Change Request Patch Set/Revision ID
        :type revision_id: str
        """
        # HTTP REST API HEADERS
        self._change_id = change_id
        self._revision_id = revision_id
        self._gerrit_con = gerrit_con

    def set_review(self, labels=None, message='', comments=None):
        """
        Endpoint to create a review for a change_id and a specific patch set
        :param labels: This is used to set +2 Code-Review for example.
        :type labels: dict
        :param message: The message will appear in the actually change-request page.
        :type message: str
        :param comments: This will become comments in the code.
        :type comments: dict
        """

        if not labels:
            labels = {}
        if not comments:
            comments = {}
        r_endpoint = "/a/changes/%s/revisions/%s/review" % (self._change_id,
                                                            self._revision_id)
        payload = {}

        if labels:
            payload['labels'] = labels
        if message:
            payload['message'] = message
        if comments:
            payload['comments'] = comments

        req = self._gerrit_con.call(
            request='post',
            r_endpoint=r_endpoint,
            r_payload=payload
        )

        status_code = req.status_code
        if status_code == 200:
            return True
        else:
            raise UnhandledError(req.content)
