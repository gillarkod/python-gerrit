#!/bin/env python

import unittest
import os
import mock
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from gerrit import Gerrit

MAX_WAIT = 10


class TestGerrit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            if os.path.isfile('./wires'):
                firefox_capabilities = DesiredCapabilities.FIREFOX
                firefox_capabilities['marionette'] = True
                firefox_capabilities['binary'] = os.environ.get('firefox_path', '/usr/bin/firefox')
            cls._browser = webdriver.Firefox()
        except WebDriverException:
            cls._browser = webdriver.Chrome()
        # Log in once to make user admin
        cls._browser.get('http://localhost:8080/login')
        cls._browser.implicitly_wait(MAX_WAIT)
        elem = cls._browser.find_element_by_id('f_user')
        elem.send_keys('felix')
        elem = cls._browser.find_element_by_id('f_pass')
        elem.send_keys('<password>' + Keys.RETURN)
        element = WebDriverWait(cls._browser, MAX_WAIT).until(
            expected_conditions.title_contains('My Reviews')
        )

    @classmethod
    def tearDownClass(cls):
        cls._browser.quit()

    def test_add_project(self):
        # Felix wants to add a project, he uses the gerrit module to do this
        gerrit = Gerrit(
            url='http://localhost:8080/',
            auth_type='http',
            auth_id='felix',
            auth_pw='<password>'
        )
        project = gerrit.create_project('my project')

        # Felix can now access his project in the web interface
        self._browser.get('http://localhost:8080/#/admin/projects/my+project')
        element = WebDriverWait(self._browser, MAX_WAIT).until(
            expected_conditions.title_contains('Project my project')
        )
        self.assertIn('Project my project', self._browser.title)
