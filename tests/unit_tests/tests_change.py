import json
import unittest
import mock
import copy

from gerrit.error import UnhandledError
from gerrit.changes.change import Change
from gerrit.projects.project import Project


class ChangeTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prefix = ')]}\''
        self._content = {
            "id":  "gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2",
            "project":  "gerritproject",
            "branch":  "master",
            "change_id":  "I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2",
            "subject":  "My change",
            "status":  "NEW",
            "created":  "2013-02-01 09:59:32.126000000",
            "updated":  "2013-02-21 11:16:36.775000000",
            "mergable":  True,
            "insertions":  34,
            "deletions":  101,
            "number":  3965,
            "owner":  {"name": "John Doe"},
        }
        self._gerrit_con = mock.Mock()

    def standard_change(self, content, status_code=200):
        if isinstance(content, list):
            self._gerrit_con.call.side_effect = content
        else:
            self._gerrit_con.call.return_value = self.prepare_request(
                content,
                status_code=status_code,
            )

        cng = Change(self._gerrit_con)
        return cng.get_change(
            self._content.get('project'),
            self._content.get('branch'),
            self._content.get('change_id'),
        )

    def prepare_request(self, content, status_code=200):
        req = mock.Mock()
        req.status_code = status_code
        req.content = '{}\n{}'.format(
            self._prefix,
            json.dumps(content)
        ).encode('utf-8')
        return req

    def test_get_change_returns_change(self):
        change = self.standard_change(
            self._content,
        )
        self.assertEqual(change.full_id, self._content.get('id'))
        self.assertEqual(change.project, self._content.get('project'))
        self.assertEqual(change.branch, self._content.get('branch'))
        self.assertEqual(change.change_id, self._content.get('change_id'))
        self.assertEqual(change.subject, self._content.get('subject'))
        self.assertEqual(change.status, self._content.get('status'))
        self.assertEqual(change.created, self._content.get('created'))
        self.assertEqual(change.updated, self._content.get('updated'))
        self.assertEqual(change.mergable, self._content.get('mergable'))
        self.assertEqual(change.insertions, self._content.get('insertions'))
        self.assertEqual(change.deletions, self._content.get('deletions'))
        self.assertEqual(change.number, self._content.get('number'))
        self.assertEqual(change.owner, self._content.get('owner'))

    def test_get_change_project_object(self):
        self._gerrit_con.call.return_value = self.prepare_request(
            self._content,
        )

        pjt = Project(self._gerrit_con)
        project = pjt.get_project('gerritproject')
        cng = Change(self._gerrit_con)
        change = cng.get_change(
            project,
            self._content.get('branch'),
            self._content.get('change_id'),
        )
        self.assertEqual(change.full_id, self._content.get('id'))

    def test_get_change_empty_project(self):
        with self.assertRaises(KeyError):
            cng = Change(self._gerrit_con)
            cng.get_change(
                '',
                self._content.get('branch'),
                self._content.get('change_id'),
            )

    def test_get_change_empty_branch(self):
        with self.assertRaises(KeyError):
            cng = Change(self._gerrit_con)
            cng.get_change(
                self._content.get('project'),
                '',
                self._content.get('change_id'),
            )

    def test_get_change_empty_change_id(self):
        with self.assertRaises(KeyError):
            cng = Change(self._gerrit_con)
            cng.get_change(
                self._content.get('project'),
                self._content.get('branch'),
                '',
            )

    def test_get_change_doesnt_exist(self):
        with self.assertRaises(ValueError):
            self.standard_change(
                dict(),
                404
            )

    def test_get_change_unhandled_error(self):
        with self.assertRaises(UnhandledError):
            self.standard_change(
                dict(),
                503
            )

    def test_create_change_success(self):
        self._gerrit_con.call.return_value = self.prepare_request(
            self._content,
            201,
        )

        with mock.patch.object(Change, 'get_change') as mock_get_change:
            cng = Change(self._gerrit_con)
            cng.create_change(
                self._content.get('project'),
                self._content.get('subject'),
                self._content.get('branch'),
                {'status': 'DRAFT'},
            )
            mock_get_change.assert_called_with(
                self._content.get('project'),
                self._content.get('branch'),
                self._content.get('change_id'),
            )

    def test_create_change_fail(self):
        self._gerrit_con.call.return_value = self.prepare_request(
            dict(),
            404,
        )

        with self.assertRaises(UnhandledError):
            cng = Change(self._gerrit_con)
            cng.create_change(
                self._content.get('project'),
                self._content.get('subject'),
                self._content.get('branch'),
                {'status': 'DRAFT'}
            )

    def test_create_change_project_object(self):
        self._gerrit_con.call.side_effect = [
            self.prepare_request(
                {"name": "gerritproject"}
            ),
            self.prepare_request(
                self._content,
                201,
            ),
        ]

        with mock.patch.object(Change, 'get_change') as mock_get_change:
            pjt = Project(self._gerrit_con)
            project = pjt.get_project('gerritproject')
            cng = Change(self._gerrit_con)
            cng.create_change(
                project,
                self._content.get('subject'),
                self._content.get('branch'),
                {'status': 'DRAFT'}
            )
            mock_get_change.assert_called_with(
                self._content.get('project'),
                self._content.get('branch'),
                self._content.get('change_id'),
            )

    def test_submit_change_success(self):
        change = self.standard_change(
            [
                self.prepare_request(
                    self._content,
                ),
                self.prepare_request(
                    {"status": "MERGED"}
                )
            ]
        )
        change.submit_change()
        self._gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint={
                'pre': '/a/changes/',
                'data': self._content.get('id'),
                'post': '/submit/',
            },
            r_payload={}
        )
        self.assertEqual(change.status, 'MERGED')

    def test_submit_change_success_with_options(self):
        change = self.standard_change(
            [
                self.prepare_request(
                    self._content,
                ),
                self.prepare_request(
                    {"status": "MERGED"}
                )
            ]
        )
        change.submit_change({'NOTIFY': 'NONE'})
        self._gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint={
                'pre': '/a/changes/',
                'data': self._content.get('id'),
                'post': '/submit/',
            },
            r_payload={'NOTIFY': 'NONE'}
        )
        self.assertEqual(change.status, 'MERGED')

    def test_submit_change_fail(self):
        change = self.standard_change(
            [
                self.prepare_request(
                    dict(),
                ),
                self.prepare_request(
                    'blocked by Verify',
                    409,
                )
            ]
        )
        with self.assertRaises(UnhandledError):
            change.submit_change()

    def test_add_reviewer(self):
        change = self.standard_change(
            [
                self.prepare_request(
                    self._content,
                ),
                self.prepare_request(
                    {"reviewers": ["my user"]},
                )
            ]
        )
        self.assertTrue(change.add_reviewer('my user'))
        self._gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint='/a/changes/{}/reviewers'.format(self._content.get('change_id')),
            r_payload={'reviewer': 'my user'},
        )

    def test_delete_reviewer(self):
        change = self.standard_change(
            [
                self.prepare_request(
                    self._content,
                ),
                self.prepare_request(
                    self._content,
                    204,
                )
            ]
        )
        self.assertTrue(change.delete_reviewer('my user'))
        self._gerrit_con.call.assert_called_with(
            request='delete',
            r_endpoint='/a/changes/{}/reviewers/my user'.format(self._content.get('change_id')),
            r_headers={},
        )

    def test_list_reviewer(self):
        change = self.standard_change(
            self._content,
        )
        change.list_reviewers()
        self._gerrit_con.call.assert_called_with(
            r_endpoint='/a/changes/{}/reviewers/'.format(self._content.get('change_id')),
        )

    def test_set_review(self):
        change = self.standard_change(
            self._content,
        )
        change.set_review()
        self._gerrit_con.call.assert_called_with(
            request='post',
            r_endpoint='/a/changes/{}/revisions/current/review'.format(self._content.get('change_id')),
            r_payload={}
        )

    def test_parent_project_quote(self):
        """Test that a quoted id is unquoted"""
        content = copy.deepcopy(self._content)
        content['id'] = 'parentproject%2Fgerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        self._gerrit_con.call.return_value = self.prepare_request(
            content,
        )

        cng = Change(self._gerrit_con)
        change = cng.get_change(
            'parentproject/gerritproject',
            self._content.get('branch'),
            self._content.get('change_id'),
        )
        self.assertEqual(
            change.full_id,
            'parentproject/{}'.format(self._content.get('id')),
        )

    def test_parent_project_no_quote(self):
        """Test that an already unquoted id is not unquoted"""
        content = copy.deepcopy(self._content)
        content['id'] = 'parentproject/gerritproject~master~I01440b5fd46a67ee38c9ef2c22eb145b8547cbb2'
        self._gerrit_con.call.return_value = self.prepare_request(
            content,
        )

        cng = Change(self._gerrit_con)
        change = cng.get_change(
            'parentproject/gerritproject',
            self._content.get('branch'),
            self._content.get('change_id'),
        )
        self.assertEqual(
            change.full_id,
            'parentproject/{}'.format(self._content.get('id')),
        )
