class GerritError(object):
    class UnhandledError(Exception):
        def __init__(self, message):
            self._msg = message

    class AuthorizationError(Exception):
        def __init__(self, message):
            self._msg = message

    class AlreadyExists(Exception):
        def __init__(self, message):
            self._msg = message

    class CredentialsNotFound(Exception):
        def __init__(self, message):
            self._msg = message
