from sqlmodel import SQLModel, Field
from datetime import date
from typing import Optional

# This is the actual database table.
class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    category: str
    amount: float
    notes: Optional[str] = None

# This is what the USER sends us when creating an expense.
# Notice: no "id" field at all — the user can never set it.                     
class ExpenseCreate(SQLModel):
    date: date
    category: str
    amount: float
    notes: Optional[str] = None

#--- Goals ---
class Goal(SQLModel, table= True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    target_amount:float
    current_amount:float=0
    target_date: Optional[date] = None
    category: Optional[str] = None

class GoalCreate(SQLModel):
    name: str
    target_amount: float
    current_amount: float = 0
    target_date: Optional[date] = None
    category: Optional[str] = None

#--- Accounts ---
class Account(SQLModel, table=True):
    id: Optional[int]= Field(default=None, primary_key=True)
    name: str 
    account_type: str
    balance: float =0 

class AccountCreate(SQLModel):
    name:str
    account_type:str
    balance: float = 0 

#--- TOODS ---
class Todo(SQLModel, table=True):
    id: Optional[int]=Field(default=None, primary_key=True)
    title:str
    due_date: Optional[date]= None
    status: str = "pending"
    priority: str ="medium"
    
class TodoCreate(SQLModel):
    title:str
    due_date: Optional[date] = None
    status : str = "pending"
    priority: str = "medium"


#--- Investments ---
class Investment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name:str
    investment_type:str
    units:float
    buy_price:float
    current_value:float

class InvestmentCreate(SQLModel):
    name: str
    investment_type: str
    units: float
    buy_price:float
    current_value:float

#--- Goal Contributions ---
class GoalContribution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    goal_id: int = Field(foreign_key="goal.id")
    date: date
    amount: float
    notes: Optional[str] = None

class GoalContributionCreate(SQLModel):
    goal_id: int
    date: date
    amount: float
    notes: Optional[str] = None