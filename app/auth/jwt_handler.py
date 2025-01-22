import time
from typing import Dict

import jwt

from app.Config import ENV_PROJECT


def token_response(
    token: str,
):
    """
    Create a dictionary response containing the access token.

    Args:
        token (str): The access token.

    Returns:
        dict: A dictionary response with the access token.

    """
    return {"access_token": token}


secret_key = ENV_PROJECT.SECRET_KEY


def sign_jwt(
    user_id: str,
    expires_after,
) -> Dict[str, str]:
    """
    Sign a JWT token for the given user ID.

    Args:
        user_id (str): The user ID to include in the JWT payload.

    Returns:
        Dict[str, str]: A dictionary response containing the access token.

    """
    # Set the expiry time to one month.
    payload = {
        "user_id": user_id,
        "expires": time.time() + expires_after,
    }  # 2592000 seconds = 30 days
    return token_response(
        jwt.encode(
            payload,
            secret_key,
            algorithm="HS256",
        )
    )


def decode_jwt(
    token: str,
) -> dict:
    """
    Decode a JWT token and return the decoded payload if the token is valid.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded JWT payload if the token is valid, an empty dictionary otherwise.

    """
    decoded_token = jwt.decode(
        token.encode(),
        secret_key,
        algorithms=["HS256"],
    )
    return decoded_token if decoded_token["expires"] >= time.time() else {}
