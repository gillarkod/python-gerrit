#!/bin/env python

import unittest
import os
import yaml
import requests
import uuid

from gerrit import Gerrit


class TestGerrit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            with open('test-config.yaml', 'r') as ymlfile:
                cls.config = yaml.load(ymlfile)
        except IOError:
            # No config file, set defaults
            cls.config = {'url': 'http://localhost:8080/',
                          'username': 'felix',
                          'password': '<password>',
                         }

        cls._url = cls.config.get('url')
        cls._admin_username = cls.config.get('admin_username')
        cls._admin_password = cls.config.get('admin_password')
        cls._user_username = cls.config.get('user_username')
        cls._user_password = cls.config.get('user_password')

        # Log in once to make Felix admin
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'username':cls._admin_username,'password':cls._admin_password}
        session_felix = requests.Session()
        session_felix.post(
            cls._url + 'login/%23/q/status%3Aopen',
            headers=headers,
            data=payload
        )

        # Log in once to make Mary accessable
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'username':cls._user_username,'password':cls._user_password}
        session_mary = requests.Session()
        session_mary.post(
            cls._url + 'login/%23/q/status%3Aopen',
            headers=headers,
            data=payload
        )

        # Generate a random name for the project
        cls._project = uuid.uuid4().hex

    def test_add_project(self):
        # Felix wants to add a project, he uses the gerrit module to do this
        gerrit = Gerrit(
            url=self._url,
            auth_type='http',
            auth_id=self._admin_username,
            auth_pw=self._admin_password,
        )
        created_project = gerrit.create_project(
            self._project,
            options={
                'description': 'my description',
                'branches': ['master'],
                'create_empty_commit': True,
            },
        )
        gotten_project = gerrit.get_project(self._project)
        # Using the same module he can get his project
        self.assertEqual(created_project, gotten_project)
        self.assertEqual(gotten_project.description, 'my description')

        # Felix uploads a new change
        change = gerrit.create_change(created_project, 'My change')

        # Wanting Mary to review the change, he adds her as a reviewer
        self.assertTrue(change.add_reviewer('mary'))

        # He can now see that Mary is a reviewer
        reviewers = change.list_reviewers()
        self.assertEqual(
            reviewers,
            [{'username': 'mary',
              'approvals': {'Code-Review': ' 0'},
              'name': 'Mary',
              '_account_id': 1000001
             }]
        )

        # Felix made a mistake, Mary shouldn't be a reviewer.
        # He removes her.
        self.assertTrue(change.delete_reviewer('mary'))

        # He can now see that Mary is no longer a reviewer
        reviewers = change.list_reviewers()
        self.assertEqual(reviewers,[])

        # Happy with the change, Felix reviews and submits it
        change.set_review(labels={'Code-Review': '+2'})
        change.submit_change()
        self.assertEqual(change.status, 'MERGED')

        # Not needing the repo anymore Felix removes it
        self.assertTrue(created_project.delete({'force': True}))

        # Felix can no longer get the project
        with self.assertRaises(ValueError):
            gerrit.get_project(self._project)
