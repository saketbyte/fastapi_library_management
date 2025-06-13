# Required FastAPI imports for routing and error handling
from fastapi import APIRouter, Depends, HTTPException, status
# Session management for DB transactions
from sqlalchemy.orm import Session
# To track current and due dates for transactions
from datetime import datetime
# Type hinting for returning multiple results
from typing import List
# ORM Models defined in models.py
import models
# Pydantic schemas for validation
import schemas
# DB session injector
from database import get_db_connection
# Middleware for authentication and admin access
from middleware import verify_token, verify_admin

# Create a new router instance for transaction-related routes
router = APIRouter()

# Route to checkout a book
@router.post("/checkout", response_model=schemas.TransactionResponse)
def checkout_book(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_token)
):
    # Fetch the book from the database
    book = db.query(models.Book).filter(models.Book.id == transaction.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # If book is not available
    if book.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book not available"
        )

    # Check if the user already has this book and hasn't returned
    existing_transaction = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.book_id == transaction.book_id,
        models.Transaction.is_returned == False
    ).first()

    if existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have this book checked out"
        )

    # If everything is valid, create a new transaction entry
    db_transaction = models.Transaction(
        user_id=current_user.id,
        book_id=transaction.book_id,
        due_date=transaction.due_date,
        checkout_date=datetime.utcnow(),
        is_returned=False
    )

    # Reduce the book quantity as one book is being issued
    book.quantity -= 1

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # Attach book details to the transaction response
    db_transaction.book = book

    return db_transaction

# Route to return a borrowed book
@router.post("/return", response_model=schemas.TransactionResponse)
def return_book_by_book_id(
    data: schemas.BookReturnById,
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_token)
):
    # Find the unreturned transaction for this user and book
    transaction = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.book_id == data.book_id,
        models.Transaction.is_returned == False
    ).first()

    # If no active transaction found
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not borrowed this book or already returned it"
        )

    # Mark the book as returned and store return date
    transaction.is_returned = True
    transaction.return_date = datetime.utcnow()

    # Increment the book quantity in DB
    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    if book:
        book.quantity += 1

    db.commit()
    db.refresh(transaction)
    transaction.book = book

    return transaction

# Route to get all books currently borrowed by the user
@router.get("/my-books", response_model=List[schemas.TransactionResponse])
def get_my_borrowed_books(
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_token)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.is_returned == False
    ).all()

    return transactions

# Admin route to get overdue transactions fore veryone
@router.get("/overdue", response_model=List[schemas.TransactionResponse])
def get_overdue_books(
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    current_time = datetime.utcnow()
    # Get all overdue unreturned transactions
    overdue_transactions = db.query(models.Transaction).filter(
        models.Transaction.due_date < current_time,
        models.Transaction.is_returned == False
    ).all()

    return overdue_transactions

# Admin route to fetch all transactions from the database table
@router.get("/", response_model=List[schemas.TransactionResponse])
def get_all_transactions(
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    transactions = db.query(models.Transaction).all()
    return transactions
