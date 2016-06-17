import unittest
import mock

from gerrit.error import UnhandledError
from gerrit.changes.revision import Revision


class RevisionTestCase(unittest.TestCase):
    def test_set_review_success(self):
        req = mock.Mock()
        req.status_code = 200
        gerrit = mock.Mock()
        gerrit.call.return_value = req
        revision = Revision(gerrit, 'my change id', 'my revision id')
        result = revision.set_review(
            labels={"Code-Review": -1},
            message='Looks good',
            comments={"README.md": [
                         {"line": 23,
                          "message": "[nit] trailing whitespace"
                         }]})
        self.assertTrue(result)
        gerrit.call.assert_called_with(
            r_endpoint='/a/changes/my change id/revisions/my revision id/review',
            r_payload={'labels': {'Code-Review': -1},
                       'message': 'Looks good',
                       'comments': {'README.md': [
                                       {'message': '[nit] trailing whitespace',
                                        'line': 23
                                       }]
                                   }
                      },
            request='post')

    def test_set_review_fail(self):
        req = mock.Mock()
        req.status_code = 404
        gerrit = mock.Mock()
        gerrit.call.return_value = req
        revision = Revision(gerrit, 'my change id', 'my revision id')
        with self.assertRaises(UnhandledError):
            result = revision.set_review()
        gerrit.call.assert_called_with(
            r_endpoint='/a/changes/my change id/revisions/my revision id/review',
            r_payload={},
            request='post'
        )
