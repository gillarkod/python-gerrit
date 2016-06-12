#!/bin/env python

import unittest
import os
import yaml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from gerrit import Gerrit

MAX_WAIT = 10


class TestGerrit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            with open('test-config.yaml', 'r') as ymlfile:
                cls.config = yaml.load(ymlfile)
        except IOError:
            # No config file, set defaults
            cls.config = {'webdriver': 'firefox',
                          'url': 'http://localhost:8080/',
                          'username': 'felix',
                          'password': '<password>',
                         }

        if cls.config.get('webdriver') == 'firefox':
            if os.path.isfile('./wires'):
                firefox_capabilities = DesiredCapabilities.FIREFOX
                firefox_capabilities['marionette'] = True
                firefox_capabilities['binary'] = os.environ.get('firefox_path', '/usr/bin/firefox')
                cls._browser = webdriver.Firefox(capabilities=firefox_capabilities)
            else:
                cls._browser = webdriver.Firefox()
        elif cls.config.get('webdriver') == 'chrome':
            cls._browser = webdriver.Chrome()
        else:
            raise Exception('Webdriver not supported')

        cls._url = cls.config.get('url')
        cls._username = cls.config.get('username')
        cls._password = cls.config.get('password')

        # Log in once to make user admin
        cls._browser.get('%slogin' % cls._url)
        cls._browser.implicitly_wait(MAX_WAIT)
        elem = cls._browser.find_element_by_id('f_user')
        elem.send_keys(cls._username)
        elem = cls._browser.find_element_by_id('f_pass')
        elem.send_keys(cls._password + Keys.RETURN)
        element = WebDriverWait(cls._browser, MAX_WAIT).until(
            expected_conditions.title_contains('My Reviews')
        )

    @classmethod
    def tearDownClass(cls):
        cls._browser.close()

    def test_add_project(self):
        # Felix wants to add a project, he uses the gerrit module to do this
        gerrit = Gerrit(
            url=self._url,
            auth_type='http',
            auth_id=self._username,
            auth_pw=self._password,
        )
        project = gerrit.create_project('my project')

        # Felix can now access his project in the web interface
        self._browser.get('%s#/admin/projects/my+project' % self._url)
        element = WebDriverWait(self._browser, MAX_WAIT).until(
            expected_conditions.title_contains('Project my project')
        )
        self.assertIn('Project my project', self._browser.title)
