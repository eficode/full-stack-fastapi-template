import uuid

from fastapi.testclient import TestClient

from app import crud
from app.core.config import settings
from app.core.db import get_table, USER_TABLE
from app.core.security import get_password_hash
from app.models import User, UserCreate
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user() -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(user_create=user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str
) -> dict[str, str]:
    """
    Return a valid token for the user with the given email.
    If the user doesn't exist it is created first.
    """
    # First check if user exists
    user = crud.get_user_by_email(email=email)
    if not user:
        password = random_lower_string()
        user_in = UserCreate(email=email, password=password, is_superuser=False)
        user = crud.create_user(user_create=user_in)
    else:
        # If user exists, reset their password
        password = random_lower_string()
        user_table = get_table(USER_TABLE)
        user_table.update_item(
            Key={"id": str(user.id)},
            UpdateExpression="SET hashed_password = :p",
            ExpressionAttributeValues={":p": get_password_hash(password)}
        )

    return user_authentication_headers(client=client, email=email, password=password)
