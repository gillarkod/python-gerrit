python-gerrit
=============
[![Build Status](https://travis-ci.org/propyless/python-gerrit.svg?branch=master)](https://travis-ci.org/propyless/python-gerrit)
[![python-gerrit on discord](https://img.shields.io/badge/discord-general@python--gerrit-738bd7.svg?style=flat)](https://discord.gg/012Ch20uOuaAtn5su)

Python module that uses the Gerrit REST API as an interface to manage changes, users, groups, and more.

# Scope
The scope of this library is to code stuff when people have a need for it.
PR's and issues are welcome if they come with unittests and 10/10 pylint.

# Usage

## Examples

# Structure
This lib will try to follow the structure the Gerrit API is structured.
For example:
```
/changes/
  change
  change edit
  reviewer
  revision
  ids
  json entities
/groups/
  group
  group member
  group include
  ids
  json entities
```

## API Reference

# Developing
Are you interested in helping out with the development of python-gerrit?

## Coding standards
We try to follow PEP8 standards to the best of our ability.

## Testing
You should be standing in the root directory of the git repository.
You will need to install the required python modules for testing.

`pip install -r test-requirements.txt`

You will also need to install a web driver for the functional tests. Put either firefox or chrome webdrivers in your path and specify it in the test-config.yaml file.

Use nosetests to run all tests. This will run both unit and function tests. It is recommended to run tests-setup.sh before this to set up your gerrit environment, please note that this requires docker.
```
./tests-setup.sh && nosetests
```
