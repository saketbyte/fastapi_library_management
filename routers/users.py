# Routing related libraries
from fastapi import APIRouter, Depends, HTTPException, status
# ORM class to maintain session with the database
from sqlalchemy.orm import Session
# For type hinting list of users
from typing import List
# Table structures for SQLAlchemy ORM
import models
# Pydantic schemas for validation and serialization
import schemas
# DB connection dependency
from database import get_db_connection
# Auth and role-based middleware
from middleware import verify_token, verify_admin, get_password_hash

# Create a new API Router instance to register all user-related routes
router = APIRouter()

# Route to get currently logged-in user details
@router.get("/me", response_model=schemas.UserResponse)
def get_current_user(current_user: models.User = Depends(verify_token)):
    # verify_token will auto-authenticate and return the current user from token
    return current_user

# Route to get all users (Admin only)
@router.get("/", response_model=List[schemas.UserResponse])
def list_users(
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    # Query to fetch all users from User table
    users = db.query(models.User).all()
    return users

# Route to get a specific user by ID (Admin only)
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    # Fetch user with given ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    # Raise error if user not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Route to update a user by ID (Admin only)
@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    # Fetch existing user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Convert Pydantic object to dictionary and update non-null fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# Route to delete user by ID (Admin only)
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db_connection),
    current_user: models.User = Depends(verify_admin)
):
    # Find user in the database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
