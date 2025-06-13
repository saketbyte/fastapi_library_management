# Routing related libraries.
from fastapi import APIRouter, Depends, HTTPException, status
# Gives the type for storing session returned by dependency for connecting to DB.
from sqlalchemy.orm import Session
from datetime import timedelta
# These are the table structures which I have defined in models.py
import models
# Pydantic schemas to define structure and validation rules.
import schemas
# To connect to the database session
from database import get_db_connection
# middleware for authentication as defined in middleware.py file.
from middleware import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# creating an instance of router which will later group the new routes created below.
router = APIRouter()


# These are decorators which will define our route and then function right next to it is executed.
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db_connection)):
    # In above line we have Depends, which injects the dependency, ie call a special function for a particular
    # purpose as soon as the request is made, we need not manually do it. It is request aware.
    # Querying the data:
    # query - function of SQL Alchemy library which is used to query the database.
    # models.User, the table structure which we have defined in models.py for accessing the correct table from db
    # filter and give the result for condition
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

# If user exists, dont make new account.
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

# Otherwise generate the passoword hash and store it in db
    hashed_password = get_password_hash(user.password)

    db_user = models.User(
        name = user.name,
        email = user.email,
        password = hashed_password,
        role = user.role
    )
#  Add the user to the database
    db.add(db_user)
    # commit() - It persists the data to the database and makes it visible to other transactions.
    # refresh() - It refreshes the data.
    db.commit()
    db.refresh(db_user)
    return db_user


# login route which will send the response of the format - response_model = some schema format
@router.post("/login", response_model=schemas.TokenWithUser)
# This route will receive request body in the format of schemas.UserLogin, and execute the dependency to connect to database.
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db_connection)):
    # Query method of sqlalchemy, filtering from the models.User table where the email matches.
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # timedelta to create a timedelta object for token validity.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #  creating the JWT
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    # returning the value of token and logged in user details for login and details to show in UI rendering.
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }
