import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import (
    CurrentUser,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.db import get_table, USER_TABLE
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    user_table = get_table(USER_TABLE)
    response = user_table.scan(
        Limit=limit,
    )
    users = response.get('Items', [])

    # Handle pagination
    if skip > 0 and skip < len(users):
        users = users[skip:]

    return UsersPublic(
        data=[UserPublic(**user) for user in users],
        count=len(users)
    )


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.create_user(user_create=user_in)
    return user


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    user_in: UserUpdateMe,
    current_user: CurrentUser,
) -> Any:
    """
    Update own user.
    """
    if user_in.email and user_in.email != current_user.email:
        user = crud.get_user_by_email(email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

    # Create update expression for DynamoDB
    update_expression = "SET "
    expression_attr_values = {}

    if user_in.full_name is not None:
        update_expression += "full_name = :full_name, "
        expression_attr_values[":full_name"] = user_in.full_name

    if user_in.email is not None:
        update_expression += "email = :email, "
        expression_attr_values[":email"] = user_in.email

    if update_expression != "SET ":
        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        user_table = get_table(USER_TABLE)
        user_table.update_item(
            Key={"id": str(current_user.id)},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attr_values
        )

        # Get updated user
        response = user_table.get_item(Key={"id": str(current_user.id)})
        user_data = response.get("Item", {})

        return User(**user_data)

    return current_user


@router.patch("/me/password")
def update_password_me(
    body: UpdatePassword, current_user: CurrentUser
) -> Message:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )

    # Update password in DynamoDB
    user_table = get_table(USER_TABLE)
    user_table.update_item(
        Key={"id": str(current_user.id)},
        UpdateExpression="SET hashed_password = :password",
        ExpressionAttributeValues={":password": get_password_hash(body.new_password)}
    )

    return Message(message="Password updated successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    # Check if user exists
    user = crud.get_user_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    # Create user
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
    )
    user = crud.create_user(user_create=user_create)

    # Send welcome email
    if settings.emails_enabled:
        email_data = generate_new_account_email(email_to=user_in.email)
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific user by id.
    """
    # Regular users can only get their own user data
    if not current_user.is_superuser and str(user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )

    # Get user by ID from DynamoDB
    user_table = get_table(USER_TABLE)
    response = user_table.get_item(Key={"id": str(user_id)})
    user_data = response.get("Item")

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return User(**user_data)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    # Get user by ID from DynamoDB
    user_table = get_table(USER_TABLE)
    response = user_table.get_item(Key={"id": str(user_id)})
    user_data = response.get("Item")

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    user = User(**user_data)

    # Check if email is being changed and is already taken
    if user_in.email and user_in.email != user.email:
        existing_user = crud.get_user_by_email(email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

    # Create update expression for DynamoDB
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    update_expression = "SET "
    expression_attr_values = {}

    for key, value in update_data.items():
        update_expression += f"{key} = :{key}, "
        expression_attr_values[f":{key}"] = value

    # Remove trailing comma and space
    if update_expression != "SET ":
        update_expression = update_expression[:-2]

        user_table.update_item(
            Key={"id": str(user_id)},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attr_values
        )

    # Get updated user
    response = user_table.get_item(Key={"id": str(user_id)})
    updated_user_data = response.get("Item", {})

    return User(**updated_user_data) if updated_user_data else user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    if str(current_user.id) == str(user_id):
        raise HTTPException(
            status_code=400,
            detail="Users can't delete themselves. Use the users/me/delete endpoint instead.",
        )

    # Delete user from DynamoDB
    user_table = get_table(USER_TABLE)
    user_table.delete_item(Key={"id": str(user_id)})

    return Message(message="User deleted successfully")


@router.delete("/me/delete")
def delete_user_me(current_user: CurrentUser) -> Message:
    """
    Delete own user.
    """
    # Delete user from DynamoDB
    user_table = get_table(USER_TABLE)
    user_table.delete_item(Key={"id": str(current_user.id)})

    return Message(message="User deleted successfully")
