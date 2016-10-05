"""
Helper
======
Helper functions
"""

import urllib
import json


def decode_json(gerrit_response):
    """
    Strip Cross Site Script Inclusion prefix from
    gerrit API response and return it as an object
    """

    return json.loads(gerrit_response.lstrip(')]}\''))

def process_endpoint(endpoint):
    """
    HTTP encode data part of endpoint if needed. If endpoint
    is a dict, endpoint and data fields are required
    :param endpoint: The endpoint to process
    :type endpoint: str/dict

    :return: Processed endpoint
    :rtype: str
    :exception: KeyError
    """
    if not isinstance(endpoint, str):
        pre = endpoint.get('pre')
        data = endpoint.get('data')
        post = endpoint.get('post')
        if pre is None or data is None:
            raise KeyError

        if post is None:
            return '%s%s/' % (
                pre,
                urllib.parse.quote(data, safe=''),
            )
        else:
            return '%s%s%s' % (
                pre,
                urllib.parse.quote(data, safe=''),
                post,
            )
    else:
        return endpoint
