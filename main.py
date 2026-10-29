from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from database import create_db_and_tables, get_session
from routers import expenses, goals, accounts, todos, investments, analytics, export, contributions
from auth import require_login
app = FastAPI(title="Life OS", dependencies=[Depends(require_login)])
@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/add", include_in_schema=False)
def add():
    return FileResponse("static/add.html")
# This runs once when the server starts up.
# It makes sure the database file and tables exist before anything else happens.
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Hello, Life OS is alive!"}

app.include_router(expenses.router)
app.include_router(goals.router)
app.include_router(accounts.router)
app.include_router(todos.router)
app.include_router(investments.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(contributions.router)