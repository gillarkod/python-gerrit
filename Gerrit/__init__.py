import json


def decode_json(gerrit_response):
    return json.loads(gerrit_response.lstrip(')]}\''))


def print_message(message, debug=True):
    if debug:
        print(message)
