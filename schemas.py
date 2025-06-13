# Importing required types and base classes for data validation and serialization
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# USER SCHEMAS

# Schema to accept data when a new user is being registered
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "user"

# Schema to accept data when a user is being updated
class UserUpdate(BaseModel):
    name: Optional[str] = None
    emai: Optional[EmailStr] = None
    role: Optional[str] = None

# Schema used to send user details back in API response
class UserResponse(BaseModel):
    id: int
    created_at: datetime
    name: str
    email: EmailStr
    role: str
    password: str = Field(exclude=True)  # Prevents password from showing in responses

    # To avoid error - TypeError: Object of type Book is not JSON serializable
    # We need to convert it to orm sql object.
    class Config:
        from_attributes = True

# Schema for login API, to accept credentials
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# BOOK SCHEMAS

# Schema to accept book details when adding a new book
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    published_year: int
    category: str
    quantity: int = 1

# Schema to accept book details when updating an existing book
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    published_year: Optional[int] = None
    category: Optional[str] = None
    quantity: Optional[int] = None

# Schema to return book data in response
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    published_year: int
    category: str
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True

# TRANSACTION SCHEMAS

# Schema to receive transaction details when user checks out a book
class TransactionCreate(BaseModel):
    book_id: int
    due_date: datetime

# Schema to return transaction data in API responses
class TransactionResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool
    book: BookResponse

    class Config:
        from_attributes = True



# Schema to return a book using only book ID
class BookReturnById(BaseModel):
    book_id: int

# AUTH / TOKEN SCHEMAS

# Schema to represent a user's data in response without password
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

# Schema for token-based login response with user details
class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# Schema used internally for extracting token data
class TokenData(BaseModel):
    email: Optional[str] = None

# PAGINATION SCHEMA

# Schema to return paginated books with meta information
class PaginationBooks(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
