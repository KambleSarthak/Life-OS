from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session, get_or_404
from models import Todo, TodoCreate

router = APIRouter(prefix="/todos", tags=["Todos"])

@router.post("/")
def create_todo(data: TodoCreate, session: Session = Depends(get_session)):
    todo = Todo.model_validate(data)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.get("/")
def read_todos(session: Session = Depends(get_session)):
    return session.exec(select(Todo)).all()

@router.get("/{todo_id}")
def read_todo(todo_id: int, session: Session = Depends(get_session)):
    return get_or_404(session, Todo, todo_id)

@router.put("/{todo_id}")
def update_todo(todo_id: int, updated: TodoCreate, session: Session = Depends(get_session)):
    todo = get_or_404(session, Todo, todo_id)
    todo.title = updated.title
    todo.due_date = updated.due_date
    todo.status = updated.status
    todo.priority = updated.priority
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/{todo_id}")
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = get_or_404(session, Todo, todo_id)
    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted"}