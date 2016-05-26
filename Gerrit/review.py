from Gerrit.error import GerritError
from Gerrit import decode_json


class Review(object):
    def __init__(self, gerrit_con, change_id, revision_id):
        # HTTP REST API HEADERS
        self._change_id = change_id
        self._revision_id = revision_id
        self._gerrit_con = gerrit_con
        self._debug = gerrit_con.debug()

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
            raise GerritError.UnhandledError(req.content)

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
        json_result = decode_json(result)
        empty_response = {'reviewers': []}

        if len(json_result.get('reviewers', False)) == 0:
            raise GerritError.AlreadyExists('The requested user \'%s\' is already an reviewer' % account_id)
        elif len(json_result.get('reviewers', False)) >= 1:
            return True
        else:
            raise GerritError.UnhandledError(json_result)

    def remove_reviewer(self, account_id):
        """
        Endpoint to remove a reviewer from a change-id
        :param account_id: Remove a user with account-id as revewier.
        :type account_id: str
        :rtype: bool
        :exception: error.AuthorizationError
        """
        r_endpoint = "/a/changes/%s/reviewers/%s" % (self._change_id, account_id)

        req = self._gerrit_con.call(request='delete',
                                    r_endpoint=r_endpoint
                                    )

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if "delete not permitted" in result:
            raise GerritError.AuthorizationError(result)

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
            raise GerritError.UnhandledError(result)

        json_result = decode_json(result)

        return json_result
