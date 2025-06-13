# Importing SQLAlchemy's core and ORM components to define table structures and relationships
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
# Importing base class from database.py to allow table class inheritance
from database import Base
# To capture the current timestamp for created_at fields
from datetime import datetime

# USER MODEL

# SQLAlchemy model to represent the 'users' table
class User(Base):
    __tablename__ = "users"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to the Transaction table, back_populates ensures bidirectional linkage
    transactions = relationship("Transaction", back_populates="user")


# BOOK MODEL

# SQLAlchemy model to represent the 'books' table
class Book(Base):
    __tablename__ = "books"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False)
    published_year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to the Transaction table
    transactions = relationship("Transaction", back_populates="book")


# TRANSACTION MODEL

# SQLAlchemy model to represent the 'transactions' table
class Transaction(Base):
    __tablename__ = "transactions"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    checkout_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    is_returned = Column(Boolean, default=False)

    # Relationships to user and book with bidirectional linkage
    user = relationship("User", back_populates="transactions")
    book = relationship("Book", back_populates="transactions")
