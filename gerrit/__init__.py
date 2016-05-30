"""
python-gerrit
=============

A module that uses the Gerrit REST API as an interface to manage
changes,users, groups, etcetera.
"""

import json


def decode_json(gerrit_response):
    """
    Strip Cross Site Script Inclusion prefix from
    gerrit API response and return it as an object
    """

    return json.loads(gerrit_response.lstrip(')]}\''))


def print_message(message, debug=True):
    """Print debug messages"""

    if debug:
        print(message)
