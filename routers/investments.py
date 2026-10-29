from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session, get_or_404
from models import Investment, InvestmentCreate

router = APIRouter(prefix="/investments", tags=["Investments"])

@router.post("/")
def create_investment(data: InvestmentCreate, session: Session = Depends(get_session)):
    investment = Investment.model_validate(data)
    session.add(investment)
    session.commit()
    session.refresh(investment)
    return investment

@router.get("/")
def read_investments(session: Session = Depends(get_session)):
    return session.exec(select(Investment)).all()

@router.get("/{investment_id}")
def read_investment(investment_id: int, session: Session = Depends(get_session)):
    return get_or_404(session, Investment, investment_id)

@router.put("/{investment_id}")
def update_investment(investment_id: int, updated: InvestmentCreate, session: Session = Depends(get_session)):
    investment = get_or_404(session, Investment, investment_id)
    investment.name = updated.name
    investment.investment_type = updated.investment_type
    investment.units = updated.units
    investment.buy_price = updated.buy_price
    investment.current_value = updated.current_value
    session.add(investment)
    session.commit()
    session.refresh(investment)
    return investment

@router.delete("/{investment_id}")
def delete_investment(investment_id: int, session: Session = Depends(get_session)):
    investment = get_or_404(session, Investment, investment_id)
    session.delete(investment)
    session.commit()
    return {"message": "Investment deleted"}