from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session, get_or_404
from models import Account, AccountCreate

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/")
def create_account(data: AccountCreate, session: Session = Depends(get_session)):
    account = Account.model_validate(data)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.get("/")
def read_accounts(session: Session = Depends(get_session)):
    return session.exec(select(Account)).all()

@router.get("/{account_id}")
def read_account(account_id: int, session: Session = Depends(get_session)):
    return get_or_404(session, Account, account_id)

@router.put("/{account_id}")
def update_account(account_id: int, updated: AccountCreate, session: Session = Depends(get_session)):
    account = get_or_404(session, Account, account_id)
    account.name = updated.name
    account.account_type = updated.account_type
    account.balance = updated.balance
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.delete("/{account_id}")
def delete_account(account_id: int, session: Session = Depends(get_session)):
    account = get_or_404(session, Account, account_id)
    session.delete(account)
    session.commit()
    return {"message": "Account deleted"}