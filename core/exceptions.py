class MocaException(Exception):
    """Base class for other exceptions"""

    @property
    def error_code(self):
        """Returns an error code to identify this type of error.
        Error code groups:
        A___ - Authentication
        """
        raise Exception("Error code is not implemented for this exception.")


class UserNotVerifiedException(MocaException):
    """The user cannot login because its account is not yet verified."""

    @property
    def error_code(self):
        return "A020"


class InvalidAuthException(MocaException):
    """Username or password wrong."""

    @property
    def error_code(self):
        return "A010"
