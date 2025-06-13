from fastapi import FastAPI, Depends, HTTPException, status
# for token based authentication
from fastapi.security import HTTPBearer
# to write in python instead of sql queries
from sqlalchemy.orm import Session
# database scheme and connection defined in another file
from database import get_db_connection, library_engine as engine
import models
# Routers defined in other file grouped below in include_router
from routers import users,books, auth, transactions
# used to verify the token.
from middleware import verify_token

from fastapi.middleware.cors import CORSMiddleware

# Refered- https://medium.com/@ddias.olv/introduction-to-fastapi-with-poetry-a-practical-guide-to-creating-a-complete-api-very-simply-e736e8691010

# Making database tables using engine created in database.py
models.Base.metadata.create_all(bind=engine)

# Initialising the application.
app = FastAPI(title="TCS - CTO Interactive Hackathon Library",
            version="1.0",
            description="Hackathon project for TCS Project hiring round",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
)

# AS I need to connect to frontend which is hosted on different url, I need to allow cross origin resource sharing.
origins = ["http://localhost:5173/", "https://lms-b3xqu5y8s-samriddh-singhs-projects.vercel.app/"] # We can allow *, or add specific URL of FE. https://lms-b3xqu5y8s-samriddh-singhs-projects.vercel.app/

app.add_middleware(CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"])

# this will be used to protect API routes based on the JWT authentication as it is passed in the header in Bearer: JWT Value
security = HTTPBearer()

# Tag is an optional parameter for documentation purposes as mentioned in FASTAPI.tianglo documentation
# adding different routers created in separate files, grouped together here.
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])


#base route
@app.get("/")
async def root():
    return {"message": "Library Management System API Up and Running! - Samriddh Singh"}


# Entrypoint, when this file is run directly, only then the below code is executed.
# This creates our entry point for the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="trace"
    )
