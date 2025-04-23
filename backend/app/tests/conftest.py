from collections.abc import Generator
import uuid
import boto3

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.db import USER_TABLE, BOOK_TABLE, create_tables_if_not_exist, get_table, dynamodb_resource
from app.main import app
from app.models import User, UserCreate
from app.core.security import get_password_hash
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def setup_dynamodb() -> Generator[None, None, None]:
    """Set up and clean up DynamoDB tables for testing"""
    # Create tables if they don't exist
    create_tables_if_not_exist()

    # Create test superuser
    user_table = get_table(USER_TABLE)
    user_id = str(uuid.uuid4())
    user_table.put_item(Item={
        "id": user_id,
        "email": settings.FIRST_SUPERUSER,
        "hashed_password": get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        "is_active": True,
        "is_superuser": True,
        "full_name": "Initial Superuser",
    })

    yield

    # Clean up after tests
    try:
        # Delete all items in tables
        user_table = get_table(USER_TABLE)
        book_table = get_table(BOOK_TABLE)

        # Scan and delete all user items
        users = user_table.scan()
        with user_table.batch_writer() as batch:
            for user in users.get('Items', []):
                batch.delete_item(Key={"id": user["id"]})

        # Scan and delete all book items
        books = book_table.scan()
        with book_table.batch_writer() as batch:
            for book in books.get('Items', []):
                batch.delete_item(Key={"id": book["id"]})
    except Exception as e:
        print(f"Error cleaning up DynamoDB tables: {e}")


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER
    )
