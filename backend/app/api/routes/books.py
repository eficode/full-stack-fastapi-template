import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser
from app.core.db import get_table, BOOK_TABLE
from app.models import Book, BookCreate, BookPublic, BooksPublic, BookUpdate, Message
from boto3.dynamodb.conditions import Key

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=BooksPublic)
def read_books(
    current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve books.
    """
    # For regular users, get only their books
    # For superusers, get all books
    book_table = get_table(BOOK_TABLE)

    if current_user.is_superuser:
        response = book_table.scan(Limit=limit)
        books = response.get('Items', [])
    else:
        # Query using the GSI for owner_id
        response = book_table.query(
            IndexName="owner_index",
            KeyConditionExpression=Key('owner_id').eq(str(current_user.id)),
            Limit=limit
        )
        books = response.get('Items', [])

    # Handle pagination
    if skip > 0 and skip < len(books):
        books = books[skip:]

    return BooksPublic(
        data=[BookPublic(**book) for book in books],
        count=len(books)
    )


@router.get("/{id}", response_model=BookPublic)
def read_book(current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get book by ID.
    """
    book_table = get_table(BOOK_TABLE)
    response = book_table.get_item(Key={"id": str(id)})
    book_data = response.get("Item")

    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found")

    book = Book(**book_data)

    # Check if user has permission to access this book
    if not current_user.is_superuser and str(book.owner_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return book


@router.post("/", response_model=BookPublic)
def create_book(
    *, current_user: CurrentUser, book_in: BookCreate
) -> Any:
    """
    Create new book.
    """
    book = crud.create_book(book_in=book_in, owner_id=current_user.id)
    return book


@router.put("/{id}", response_model=BookPublic)
def update_book(
    *, current_user: CurrentUser, id: uuid.UUID, book_in: BookUpdate
) -> Any:
    """
    Update a book.
    """
    book_table = get_table(BOOK_TABLE)
    response = book_table.get_item(Key={"id": str(id)})
    book_data = response.get("Item")

    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found")

    book = Book(**book_data)

    # Check if user has permission to update this book
    if not current_user.is_superuser and str(book.owner_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Create update expression for DynamoDB
    update_data = book_in.model_dump(exclude_unset=True)

    update_expression = "SET "
    expression_attr_values = {}

    for key, value in update_data.items():
        if value is not None:  # Only update non-None values
            update_expression += f"{key} = :{key}, "
            expression_attr_values[f":{key}"] = value

    # Remove trailing comma and space
    if update_expression != "SET ":
        update_expression = update_expression[:-2]

        book_table.update_item(
            Key={"id": str(id)},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attr_values
        )

    # Get updated book
    response = book_table.get_item(Key={"id": str(id)})
    updated_book_data = response.get("Item", {})

    return Book(**updated_book_data) if updated_book_data else book


@router.delete("/{id}")
def delete_book(
    *, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a book.
    """
    book_table = get_table(BOOK_TABLE)
    response = book_table.get_item(Key={"id": str(id)})
    book_data = response.get("Item")

    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found")

    book = Book(**book_data)

    # Check if user has permission to delete this book
    if not current_user.is_superuser and str(book.owner_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Delete the book
    book_table.delete_item(Key={"id": str(id)})

    return Message(message="Book deleted successfully")
