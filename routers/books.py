# Routing related libraries.
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
# logical or
from sqlalchemy import or_
# typing.Optional Optional[X] is equivalent to X | None (or Union[X, None]). used for type hinting
from typing import Optional, List

import models
# Pydantic schemas to define structure and validation rules.
import schemas
# To connect to the database session
from database import get_db_connection
# middleware for authentication as defined in middleware.py file.
from middleware import verify_token, verify_admin
import math

# A router instance
router = APIRouter()

# response will be bookresponse type from model.
@router.post("/",response_model=schemas.BookResponse)
#  Dependency to connect to the database and will receive request body of type BookCreate
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db_connection), current_user: models.User = Depends(verify_admin)):
    db_book = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()

    if db_book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already exists")

    db_book = models.Book(**book.dict()) # This syntax is to unpack the dictionary into key = value format with , sep
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book

# get route for searching all the books, tried to implement pagination as well.
@router.get("/", response_model=schemas.PaginationBooks)
def list_books(
    page:int = Query(1,ge=1),
    per_page: int = Query(10, ge=1, le=100),
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    isbn: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    published_year: Optional[int] = Query(None),
    db: Session = Depends(get_db_connection)
    ):

    query = db.query(models.Book)

#  Filter based on query made after fetching all the books.
    if title:
        query = query.filter(models.Book.title.contains(title))
    if author:
        query = query.filter(models.Book.author.contains(author))
    if isbn:
        query = query.filter(models.Book.isbn.contains(isbn))
    if category:
        query = query.filter(models.Book.category.contains(category))
    if published_year:
        query = query.filter(models.Book.published_year == published_year)


#  simple math logic for pagination, remainder factor theorem
    total_books = query.count()
    total_pages = math.ceil(total_books / per_page)
# have to do .all() to receive the result as list
    books = query.offset((page - 1) * per_page).limit(per_page).all()

    return {"books": books, "total": total_books, "total_pages": total_pages, "per_page": per_page, "page": page}


#  Search based on specific requirement
@router.get("/search", response_model=List[schemas.BookResponse])
def search_books( q: str = Query(..., description="Search Keywrod for query"), db: Session = Depends(get_db_connection)):

    books = db.query(models.Book).filter(or_(
        models.Book.title.contains(q),
        models.Book.author.contains(q),
        models.Book.isbn.contains(q),
    )).limit(20).all()

    return books


#  Update request which will receive  book id and book update in BookUpdate schema.
# response willbe of updated books.
@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
# To avoid over-writing the fields with None / null values we use exclude unset = true
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        # setattr(object, attribute_name, value) book is the object, and filed value as key val pairs
        setattr(book, field, value) # helped to avoid hard-coding values.

    db.commit()
    db.refresh(book)
    return book

#  Deletion route for book deleting through the book id as path parameter accessible only to admin.
@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}