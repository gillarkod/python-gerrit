python-gerrit
=============
[![Build Status](https://travis-ci.org/propyless/python-gerrit.svg?branch=master)](https://travis-ci.org/propyless/python-gerrit)

Python module that uses the Gerrit REST API as an interface to manage changes, users, groups, and more.

# Usage

## Examples

## API Reference

# Developing
Are you interested in helping out with the development of python-gerrit?

## Coding standards
We try to follow PEP8 standards to the best of our ability.

## Testing
You should be standing in the root directory of the git repository.
You will need to install the required python modules for testing.

`pip install -r test-requirements.txt`

This folder needs to be in the PYTHONPATH so that python can find the Gerrit module. Then run the tests.
```
PYTHONPATH=$(pwd)
python tests/tests_Gerrit.py
```
