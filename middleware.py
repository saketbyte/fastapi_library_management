from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# Depends is FastAPI's way of injecting reusable logic into application.
#  A dependency is simply a function that performs some operation and returns a value,
#  which can then be used by any endpoint.


# Refer - https://medium.com/@ddias.olv/mastering-depends-in-fastapi-unlocking-the-power-of-dependency-injection-e529c99386ea

#  https://fastapi.tiangolo.com/tutorial/dependencies/#what-is-dependency-injection

# Using orm to connect and perform operations on sqllite
from sqlalchemy.orm import Session
# for token based authentication
# JSON Object signing and encryption
from jose import JWTError, jwt
# Date objects in a particular format.
from datetime import datetime, timedelta
# For hashing the password.
from passlib.context import CryptContext
import models
from database import get_db_connection

SECRET_KEY = "FASTAPI_PROJECT"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This line creates an object of HTTPBearer class
# to handle HTTP Bearer authentication.
# It is used to protect routes by  a valid JWT token in the "Authorization" header.
security = HTTPBearer()


# Steps to do

# verify password

# Using the same key to check our hash value verification.
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# get password in hashed format
def get_password_hash(password):
    return pwd_context.hash(password)

#  create jwt access tokens - takes in email and password to generate JWT
def create_access_token(data:dict, expires_delta: timedelta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# verify the token


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session= Depends(get_db_connection)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers= {"WWW-Authenticate":"Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception


    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None:
        raise credentials_exception
    return user

# Verify the admin user type for protected routes
def verify_admin(current_user:models.User = Depends(verify_token)):
    if(current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No admin rights to perform requested action")
    return current_user
