from sqlmodel import SQLModel, create_engine, Session
from fastapi import HTTPException
DATABASE_URL="sqlite:///life_os.db"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_or_404(session, model, item_id):
    item = session.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return item
