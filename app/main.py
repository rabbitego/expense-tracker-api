from fastapi import FastAPI

from app.database import engine, Base
from app.routers import auth, expenses

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense Tracker API",
    description="A REST API for tracking personal expenses with JWT authentication",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(expenses.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Expense Tracker API is running", "docs": "/docs"}
