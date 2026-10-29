from fastapi import APIRouter, Depends
from sqlmodel import Session, select 
from database import get_session, get_or_404
from models import Expense, ExpenseCreate

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post("/")
def create_expense(expense_data: ExpenseCreate, session: Session = Depends(get_session)):
    expense = Expense.model_validate(expense_data)  
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense

@router.get("/")
def read_expenses(session:Session = Depends(get_session)):
    return session.exec(select(Expense)).all()

@router.get("/{expense_id}")
def read_expense(expense_id: int, session: Session = Depends(get_session)):
    return get_or_404(session, Expense, expense_id)

@router.put("/{expense_id}")
def update_expense(expense_id: int, updated: ExpenseCreate, session: Session =Depends(get_session)):
    expense = get_or_404(session, Expense, expense_id)
    expense.data =updated.date
    expense.category = updated.category
    expense.amount = updated.amount
    expense.notes=updated.notes
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense
 
@router.delete("/{expense_id}")
def delete_expense(expense_id: int, session: Session = Depends(get_session)):
    expense = get_or_404(session, Expense, expense_id)
    session.delete(expense)
    session.commit()
    return{"message":"Expense deleted"}
