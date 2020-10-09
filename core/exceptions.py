class MocaException(Exception):
    """Base class for other exceptions"""

    @property
    def error_code(self):
        """Returns an error code to identify this type of error.
        Error code groups:
        A___ - Authentication
        """
        raise Exception("Error code is not implemented for this exception.")

    @property
    def http_code(self):
        """The HTTP code which should be returned to the client."""
        return 500


class UserNotVerifiedException(MocaException):
    """The user cannot login because its account is not yet verified."""

    @property
    def error_code(self):
        return "AL020"

    @property
    def http_code(self):
        """The HTTP code which should be returned to the client."""
        return 401


class InvalidAuthException(MocaException):
    """Username and/or password wrong."""

    @property
    def error_code(self):
        return "AL010"

    @property
    def http_code(self):
        """The HTTP code which should be returned to the client."""
        return 401


class UsernameAlreadyTakenException(MocaException):
    """Username already taken."""

    @property
    def error_code(self):
        return "AR010"

    @property
    def http_code(self):
        """The HTTP code which should be returned to the client."""
        return 409
