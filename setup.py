#!/usr/bin/python

import os

from setuptools import (
    setup,
    find_packages,
)

repoRootPath = os.path.dirname(os.path.abspath(__file__))
versionFile = os.path.join(repoRootPath, 'VERSION')


def get_version():
    f = open(versionFile)
    ver = f.readline().strip('\n')
    f.close()
    return ver


setup(
    name="python-gerrit",
    version=get_version(),
    author="propyless@github",
    license='Apache License 2.0',
    packages=find_packages('.'),
    include_package_data=True,
    url='https://github.com/propyless/python-gerrit',
    description='python-gerrit is a module that interfaces with Gerrits REST API.',
    install_requires=[
        "requests"
    ],
)
