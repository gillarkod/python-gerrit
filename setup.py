"""
Setup file used for pypi
"""
import os
from setuptools import (
    setup,
    find_packages,
)

REPOROOTPATH = os.path.dirname(os.path.abspath(__file__))
VERSIONFILE = os.path.join(REPOROOTPATH, 'VERSION')


def get_version():
    """
    Get the current version
    :return: str of version
    """
    with open(VERSIONFILE) as file:
        return file.readline().strip('\n')

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
