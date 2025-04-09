import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.book import create_random_book


def test_create_book(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "title": "Test Book",
        "description": "A test book description",
        "published_year": 2024,
        "isbn": "123-456-789",
        "pages": 200,
        "price": 29.99
    }
    response = client.post(
        f"{settings.API_V1_STR}/books/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["published_year"] == data["published_year"]
    assert content["isbn"] == data["isbn"]
    assert content["pages"] == data["pages"]
    assert content["price"] == data["price"]
    assert "id" in content
    assert "owner_id" in content


def test_read_book(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    book = create_random_book(db)
    response = client.get(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == book.title
    assert content["description"] == book.description
    assert content["id"] == str(book.id)
    assert content["owner_id"] == str(book.owner_id)
    assert content["published_year"] == book.published_year
    assert content["isbn"] == book.isbn
    assert content["pages"] == book.pages
    assert content["price"] == book.price


def test_read_book_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/books/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Book not found"


def test_read_book_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    book = create_random_book(db)
    response = client.get(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_books(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_book(db)
    create_random_book(db)
    response = client.get(
        f"{settings.API_V1_STR}/books/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_book(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    book = create_random_book(db)
    data = {
        "title": "Updated title",
        "description": "Updated description",
        "published_year": 2025,
        "isbn": "987-654-321",
        "pages": 300,
        "price": 39.99
    }
    response = client.put(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["published_year"] == data["published_year"]
    assert content["isbn"] == data["isbn"]
    assert content["pages"] == data["pages"]
    assert content["price"] == data["price"]
    assert content["id"] == str(book.id)
    assert content["owner_id"] == str(book.owner_id)


def test_update_book_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "title": "Updated title",
        "description": "Updated description",
        "published_year": 2025,
        "isbn": "987-654-321",
        "pages": 300,
        "price": 39.99
    }
    response = client.put(
        f"{settings.API_V1_STR}/books/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Book not found"


def test_update_book_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    book = create_random_book(db)
    data = {
        "title": "Updated title",
        "description": "Updated description",
        "published_year": 2025,
        "isbn": "987-654-321",
        "pages": 300,
        "price": 39.99
    }
    response = client.put(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_book(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    book = create_random_book(db)
    response = client.delete(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Book deleted successfully"


def test_delete_book_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/books/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Book not found"


def test_delete_book_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    book = create_random_book(db)
    response = client.delete(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
