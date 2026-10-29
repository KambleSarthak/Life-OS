from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Goal, GoalContribution, GoalContributionCreate

router = APIRouter(prefix="/contributions", tags=["Contributions"])


@router.post("/")
def add_contribution(data: GoalContributionCreate, session: Session = Depends(get_session)):
    goal = session.get(Goal, data.goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    contribution = GoalContribution.model_validate(data)
    goal.current_amount += data.amount  # keep the goal's saved total in sync
    session.add(contribution)
    session.add(goal)
    session.commit()
    session.refresh(contribution)
    return contribution


@router.get("/")
def list_contributions(goal_id: Optional[int] = None, session: Session = Depends(get_session)):
    query = select(GoalContribution).order_by(GoalContribution.date.desc())
    if goal_id is not None:
        query = query.where(GoalContribution.goal_id == goal_id)
    return session.exec(query).all()


@router.delete("/{contribution_id}")
def delete_contribution(contribution_id: int, session: Session = Depends(get_session)):
    contribution = session.get(GoalContribution, contribution_id)
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    goal = session.get(Goal, contribution.goal_id)
    if goal:
        goal.current_amount -= contribution.amount
        session.add(goal)
    session.delete(contribution)
    session.commit()
    return {"message": "Contribution deleted"}