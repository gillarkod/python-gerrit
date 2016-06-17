#!/bin/env python

import unittest
import os
import yaml
import requests

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
        cls._username = cls.config.get('username')
        cls._password = cls.config.get('password')

        # Log in once to make user admin
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'username':cls._username,'password':cls._password}
        session = requests.Session()
        session.post(cls._url + 'login/%23/q/status%3Aopen',
                     headers=headers,
                     data=payload)

    def test_add_project(self):
        # Felix wants to add a project, he uses the gerrit module to do this
        gerrit = Gerrit(
            url=self._url,
            auth_type='http',
            auth_id=self._username,
            auth_pw=self._password,
        )
        created_project = gerrit.create_project(
            'my project',
            options={'description': 'my description'},
        )
        gotten_project = gerrit.get_project('my project')
        # Using the same module he can get his project
        self.assertEqual(created_project, gotten_project)
        self.assertEqual(gotten_project.description, 'my description')

        # Not needing the repo anymore Felix removes it
        self.assertTrue(created_project.delete())

        # Felix can no longer get the project
        with self.assertRaises(ValueError):
            gerrit.get_project('my project')
