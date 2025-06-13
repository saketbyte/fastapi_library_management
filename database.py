from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# POC related database url for sqllite support built in python
SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"

# Createing and configuring the engine which establishes connection
library_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# print(library_engine.list_table_names())

# Creating the session
SessionLocal = sessionmaker(autocommit  = False, autoflush = False, bind = library_engine)

# Creating the base class This will be used in models.py later and then models in main.py
Base = declarative_base()

def get_db_connection():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()