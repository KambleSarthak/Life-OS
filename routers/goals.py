from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session, get_or_404
from models import Goal, GoalCreate

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.post("/")
def create_goal(data: GoalCreate, session: Session = Depends(get_session)):
    goal = Goal.model_validate(data)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal

@router.get("/")
def read_goals(session: Session = Depends(get_session)):
    return session.exec(select(Goal)).all()

@router.get("/{goal_id}")
def read_goal(goal_id: int, session: Session = Depends(get_session)):
    return get_or_404(session, Goal, goal_id)

@router.put("/{goal_id}")
def update_goal(goal_id: int, updated: GoalCreate, session: Session = Depends(get_session)):
    goal = get_or_404(session, Goal, goal_id)
    goal.name = updated.name
    goal.target_amount = updated.target_amount
    goal.current_amount = updated.current_amount
    goal.target_date = updated.target_date
    goal.category = updated.category
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, session: Session = Depends(get_session)):
    goal = get_or_404(session, Goal, goal_id)
    session.delete(goal)
    session.commit()
    return {"message": "Goal deleted"}