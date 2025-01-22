from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt_handler import decode_jwt


def verify_jwt(
    jwtoken: str,
) -> bool:
    """
    Verify the JWT token.

    Args:
        jwtoken (str): The JWT token to verify.

    Returns:
        bool: True if the token is valid, False otherwise.

    """
    try:
        isTokenValid: bool = False

        payload = decode_jwt(jwtoken)
        if payload:
            isTokenValid = True
        return isTokenValid
    except:
        raise HTTPException(
            403,
            "Invalid token or expired token",
        )


class JWTBearer(HTTPBearer):
    """
    Custom FastAPI Bearer token class for JWT authentication.

    Args:
        auto_error (bool): Whether to raise an HTTPException automatically on authentication failure.

    """

    def __init__(
        self,
        auto_error: bool = True,
    ):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Validate and extract the JWT token from the request.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            str: The JWT token if valid.

        Raises:
            HTTPException: If the token is invalid or missing.

        """
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(
            request
        )
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403,
                    detail="Invalid authentication token",
                )

            if not verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail="Invalid token or expired token",
                )

            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403,
                detail="Invalid authorization token",
            )
