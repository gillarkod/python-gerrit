"""
Helper class for common test functions
"""
from unittest import TestCase
from json import dumps


class GerritUnitTest(TestCase):
    """
    Helper class for common test functions
    """
    URL = 'http://example.com'
    USERNAME = 'user_found'
    PASSWORD = 'password_found'
    PROJECT = 'gerritproject'
    BRANCH = 'master'
    CHANGE_ID = 'I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
    FULL_ID = '{}~{}~{}'.format(
        PROJECT,
        BRANCH,
        CHANGE_ID,
    )
    FULL_ID_QUOTED = '{}%7E{}%7E{}'.format(
        PROJECT,
        BRANCH,
        CHANGE_ID,
    )
    REVISION_ID = 'my revision id'
    PARENT = 'parentproject'
    SUBJECT = 'My change'
    DESCRIPTION = 'My gerrit project'
    STATUS = 'NEW'
    STATE = 'ACTIVE'
    CREATED = '2013-02-01 09:59:32.126000000'
    UPDATED = '2013-02-21 11:16:36.775000000'
    MERGABLE = True
    INSERTIONS = 34
    DELETIONS = 101
    NUMBER = 3965
    OWNER = {'name': 'John Doe'}
    USER = 'my user'

    @staticmethod
    def build_response(content=None):
        """
        Builds a response that emulates gerrit format
        :param content: The content that should be encoded
        :return: str of encoded content
        """
        if content is None:
            return ')]}\''.encode('utf-8')
        else:
            return ')]}}\'{}'.format(dumps(content)).encode('utf-8')
