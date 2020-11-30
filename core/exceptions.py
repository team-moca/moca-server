class MocaException(Exception):
    """Base class for other exceptions"""

    @property
    def error_code(self):
        """Returns an error code to identify this type of error.
        Error code groups:

        A____ - Authentication
        AR___   - Registration
        AL___   - Login

        GX___ - Generic exceptions (mostly http exceptions)
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


class TimeoutException(MocaException):
    """Timeout."""

    @property
    def error_code(self):
        return "IT010"

    @property
    def http_code(self):
        """The HTTP code which should be returned to the client."""
        return 504


class NotFoundException(MocaException):
    """Generic not found."""

    @property
    def error_code(self):
        return "GX404"

    @property
    def http_code(self):
        """The HTTP code which should be returned to the client."""
        return 404
