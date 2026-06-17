from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from collections import defaultdict

from app.database import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseStats
from app.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = Expense(**expense_data.model_dump(), owner_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Expense).filter(Expense.owner_id == current_user.id)

    if category:
        query = query.filter(Expense.category == category)
    if min_amount is not None:
        query = query.filter(Expense.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Expense.amount <= max_amount)

    return query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()


@router.get("/stats", response_model=ExpenseStats)
def get_expense_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expenses = db.query(Expense).filter(Expense.owner_id == current_user.id).all()

    if not expenses:
        return ExpenseStats(
            total_spent=0,
            average_expense=0,
            expense_count=0,
            top_category="N/A",
            by_category={},
        )

    by_category = defaultdict(float)
    for exp in expenses:
        by_category[exp.category] += exp.amount

    total = sum(exp.amount for exp in expenses)
    top_category = max(by_category, key=by_category.get)

    return ExpenseStats(
        total_spent=round(total, 2),
        average_expense=round(total / len(expenses), 2),
        expense_count=len(expenses),
        top_category=top_category,
        by_category=dict(by_category),
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.owner_id == current_user.id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.owner_id == current_user.id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_fields = expense_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.owner_id == current_user.id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
