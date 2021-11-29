"""Module for custom exceptions.

Where possible we try to throw exceptions with non-generic,
meaningful names.
"""


class GerritAPIException(Exception):
    """
    Base class for all errors
    """

    pass


class ClientError(GerritAPIException):
    pass


class ServerError(GerritAPIException):
    pass


class UnauthorizedError(GerritAPIException):
    """
    401 Unauthorized
    """

    pass


class AuthError(ClientError):
    """
    403 Forbidden is returned if the operation is not allowed because the calling user does not have sufficient permissions.
    """

    pass


class ValidationError(ClientError):
    """
    400 Bad Request is returned if the request is not understood by the server due to malformed syntax.
    E.g. 400 Bad Request is returned if JSON input is expected but the 'Content-Type' of the request is not 'application/json' or the request body doesn't contain valid JSON.
    400 Bad Request is also returned if required input fields are not set or if options are set which cannot be used together.
    """

    pass


class NotAllowedError(ClientError):
    """
    405 Method Not Allowed is returned if the resource exists but doesn't support the operation.
    """

    pass


class ConflictError(ClientError):
    """
    409 Conflict is returned if the request cannot be completed because the current state of the resource doesn't allow the operation.
    """

    pass


class NotFoundError(ClientError):
    """
    Resource cannot be found
    """

    pass


class UnknownBranch(KeyError, NotFoundError):
    """
    Gerrit does not recognize the branch requested.
    """

    pass


class UnknownTag(KeyError, NotFoundError):
    """
    Gerrit does not recognize the tag requested.
    """

    pass


class UnknownFile(KeyError, NotFoundError):
    """
    Gerrit does not recognize the revision file requested.
    """

    pass


class UnsupportMethod(Exception):
    """
    This Error will be raised when program calls methods or parameters that are currently unsupported
    """

    pass
