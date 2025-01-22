from fastapi import HTTPException, status
from fastapi.responses import ORJSONResponse
from loguru import logger
from starlette.requests import Request


async def http_error_handler(request: Request, exc: HTTPException) -> ORJSONResponse:
    logger.error(exc.detail)
    return ORJSONResponse({"message": exc.detail}, status_code=exc.status_code)


class CredentialsInvalidException(HTTPException):
    """
    Exception raised when credentials provided by the user are invalid.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ResourceNotFoundException(HTTPException):
    """
    Exception raised when a requested resource is not found.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found.",
        )


class ResourceConflictException(HTTPException):
    """
    Exception raised when there is a conflict with the requested resource.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource Conflict.",
        )


class InternalServerErrorException(HTTPException):
    """
    Exception raised when an internal server error occurs.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Error.",
        )


class BadRequestException(HTTPException):
    """
    Exception raised when the client's request is malformed.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request.",
        )


class ForbiddenException(HTTPException):
    """
    Exception raised when the server understands the request but refuses to authorize it.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )


class InvalidSubscription(HTTPException):
    """
    Exception raised when the subscription is not found or is invalid.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Invalid Subscription.",
        )
