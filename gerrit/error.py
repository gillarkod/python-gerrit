"""
Error
=====

Errors for python-gerrit
"""


class UnhandledError(Exception):
    """Raise for unhandled errors"""


class AuthorizationError(Exception):
    """Raise for when authorization fails"""


class AlreadyExists(Exception):
    """Raise for when an object already exists"""


class CredentialsNotFound(Exception):
    """Raise for when an credentials can't be found"""
