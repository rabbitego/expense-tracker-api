# Expense Tracker API

A RESTful API built with **FastAPI** for tracking personal expenses. Features JWT authentication, expense categorization, filtering, and spending analytics.

## Features

- **User Authentication** - Register and login with JWT tokens
- **CRUD Operations** - Create, read, update, and delete expenses
- **Filtering** - Filter expenses by category, amount range
- **Spending Stats** - Get total spending, averages, and category breakdowns
- **Pagination** - Built-in pagination for expense lists
- **Auto Docs** - Interactive API documentation at `/docs`

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database (swap to PostgreSQL for production)
- **Pydantic** - Data validation and serialization
- **JWT** - Secure token-based authentication
- **Pytest** - Unit and integration tests

## Quick Start

```bash
# Clone the repo
git clone https://github.com/rabbitego/expense-tracker-api.git
cd expense-tracker-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive docs at `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create a new user account |
| POST | `/auth/login` | Login and get JWT token |
| POST | `/expenses/` | Add a new expense |
| GET | `/expenses/` | List all expenses (with filters) |
| GET | `/expenses/stats` | Get spending statistics |
| GET | `/expenses/{id}` | Get a specific expense |
| PUT | `/expenses/{id}` | Update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |

## Running Tests

```bash
pytest tests/ -v
```

## Example Usage

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@email.com", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=john&password=secret123"

# Add expense (use token from login response)
curl -X POST http://localhost:8000/expenses/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 15.99, "category": "Food", "description": "Coffee and bagel"}'

# Get spending stats
curl http://localhost:8000/expenses/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```
