import uuid

from pydantic import BaseModel, EmailStr, Field


# Shared properties - using Pydantic BaseModel instead of SQLModel
class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Model for user data in DynamoDB
class User(UserBase):
    id: uuid.UUID | str
    hashed_password: str

    class Config:
        from_attributes = True


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID | str


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int


# Shared properties for book model
class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    published_year: int | None = None
    isbn: str | None = None
    pages: int | None = None
    price: float | None = None


# Properties to receive on book creation
class BookCreate(BookBase):
    pass


# Properties to receive on book update
class BookUpdate(BookBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    published_year: int | None = None
    isbn: str | None = None
    pages: int | None = None
    price: float | None = None


# Model for book data in DynamoDB
class Book(BookBase):
    id: uuid.UUID | str
    owner_id: uuid.UUID | str

    class Config:
        from_attributes = True


# Properties to return via API, id is always required
class BookPublic(BookBase):
    id: uuid.UUID | str
    owner_id: uuid.UUID | str


class BooksPublic(BaseModel):
    data: list[BookPublic]
    count: int


# Generic message
class Message(BaseModel):
    message: str


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: str | None = None


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
