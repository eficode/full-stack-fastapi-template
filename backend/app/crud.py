import uuid
from typing import Any

from boto3.dynamodb.conditions import Key

from app.core.db import get_table
from app.core.constants import BOOK_TABLE, USER_TABLE
from app.core.security import get_password_hash, verify_password
from app.models import Book, BookCreate, User, UserCreate, UserUpdate


def create_user(*, user_create: UserCreate) -> User:
    """Create a new user in DynamoDB"""
    user_id = str(uuid.uuid4())

    user_data = {
        "id": user_id,
        "email": user_create.email,
        "hashed_password": get_password_hash(user_create.password),
        "full_name": user_create.full_name,
        "is_active": user_create.is_active,
        "is_superuser": user_create.is_superuser
    }

    user_table = get_table(USER_TABLE)
    user_table.put_item(Item=user_data)

    return User(**user_data)


def update_user(*, db_user: User, user_in: UserUpdate) -> Any:
    """Update a user in DynamoDB"""
    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]

    # Prepare update expression and attribute values
    update_expression = "SET "
    expression_attr_values = {}

    for key, value in update_data.items():
        update_expression += f"{key} = :{key}, "
        expression_attr_values[f":{key}"] = value

    # Remove trailing comma and space
    if update_expression != "SET ":
        update_expression = update_expression[:-2]

        user_table = get_table(USER_TABLE)
        user_table.update_item(
            Key={"id": str(db_user.id)},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attr_values
        )

    # Get updated user
    response = user_table.get_item(Key={"id": str(db_user.id)})
    user_data = response.get("Item", {})

    return User(**user_data) if user_data else None


def get_user_by_email(*, email: str) -> User | None:
    """Get a user by email from DynamoDB"""
    user_table = get_table(USER_TABLE)

    response = user_table.query(
        IndexName="email_index",
        KeyConditionExpression=Key("email").eq(email)
    )

    items = response.get("Items", [])
    if not items:
        return None

    return User(**items[0])


def authenticate(*, email: str, password: str) -> User | None:
    """Authenticate a user by email and password"""
    user = get_user_by_email(email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_book(*, book_in: BookCreate, owner_id: uuid.UUID) -> Book:
    """Create a new book in DynamoDB"""
    book_id = str(uuid.uuid4())

    book_data = {
        "id": book_id,
        "owner_id": str(owner_id),
        **book_in.model_dump(),
    }

    book_table = get_table(BOOK_TABLE)
    book_table.put_item(Item=book_data)

    return Book(**book_data)
