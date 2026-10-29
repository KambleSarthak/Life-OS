from datetime import date, timedelta 
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from models import Expense, Goal, Account, Investment, GoalContribution 

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ---------- 1. Spending by category for a month ----------
@router.get("/expenses/by-category")
def expenses_by_category(
    year: Optional[int] = None,
    month: Optional[int] = None,
    session: Session = Depends(get_session),
):
    today = date.today()
    year = year or today.year
    month = month or today.month

    expenses = session.exec(select(Expense)).all()
    empty = {"year": year, "month": month, "total": 0, "by_category": []}
    if not expenses:
        return empty

    # Turn database rows into a pandas table (DataFrame)
    df = pd.DataFrame([e.model_dump() for e in expenses])
    df["date"] = pd.to_datetime(df["date"])
    df["category"] = df["category"].str.strip().str.title()  # "FOOD" and "food" become "Food"

    # Keep only the requested month
    df = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]
    if df.empty:
        return empty

    # Group by category, add up amounts, biggest first
    grouped = df.groupby("category")["amount"].sum().sort_values(ascending=False)

    return {
        "year": year,
        "month": month,
        "total": float(grouped.sum()),
        "by_category": [
            {"category": cat, "amount": float(amt)} for cat, amt in grouped.items()
        ],
    }


# ---------- 2. Goal progress ----------
@router.get("/goals/progress")
def goal_progress(session: Session = Depends(get_session)):
    goals = session.exec(select(Goal)).all()
    today = date.today()
    results = []

    for g in goals:
        percent = round(g.current_amount / g.target_amount * 100, 1) if g.target_amount else 0
        remaining = max(g.target_amount - g.current_amount, 0)

        item = {
            "id": g.id,
            "name": g.name,
            "target_amount": g.target_amount,
            "current_amount": g.current_amount,
            "percent_complete": percent,
            "remaining": remaining,
        }

        if g.target_date:
            days_left = (g.target_date - today).days
            item["target_date"] = g.target_date
            item["days_left"] = days_left
            if days_left > 0 and remaining > 0:
                months_left = days_left / 30.44
                item["needed_per_month"] = round(remaining / months_left, 2)
            elif days_left <= 0 and remaining > 0:
                item["status"] = "overdue"

        results.append(item)

    return results


# ---------- 3. Net worth summary ----------
@router.get("/summary")
def summary(session: Session = Depends(get_session)):
    accounts = session.exec(select(Account)).all()
    investments = session.exec(select(Investment)).all()

    cash_total = sum(a.balance for a in accounts)
    invested = sum(i.units * i.buy_price for i in investments)
    current_value = sum(i.units * i.current_value for i in investments)
    gain = current_value - invested

    return {
        "accounts_total": round(cash_total, 2),
        "invested_amount": round(invested, 2),
        "investments_current_value": round(current_value, 2),
        "investment_gain": round(gain, 2),
        "investment_gain_percent": round(gain / invested * 100, 2) if invested else 0,
        "net_worth": round(cash_total + current_value, 2),
    }

    # ---------- 4. Goal projection (based on your real saving pace) ----------
@router.get("/goals/projection")
def goal_projection(session: Session = Depends(get_session)):
    today = date.today()
    goals = session.exec(select(Goal)).all()
    results = []

    for g in goals:
        remaining = max(g.target_amount - g.current_amount, 0)
        item = {
            "id": g.id,
            "name": g.name,
            "remaining": remaining,
            "target_date": g.target_date,
        }

        if remaining == 0:
            item["status"] = "completed"
            results.append(item)
            continue

        contribs = session.exec(
            select(GoalContribution).where(GoalContribution.goal_id == g.id)
        ).all()
        if not contribs:
            item["status"] = "no_data"
            item["message"] = "Log some contributions to see a projection."
            results.append(item)
            continue

        # Pace = money added in a recent window (30 to 90 days) / months in that window
        first = min(c.date for c in contribs)
        window_days = min(max((today - first).days, 30), 90)
        window_start = today - timedelta(days=window_days)
        recent_total = sum(c.amount for c in contribs if c.date >= window_start)
        monthly_pace = recent_total / (window_days / 30.44)
        item["monthly_pace"] = round(monthly_pace, 2)

        if monthly_pace <= 0:
            item["status"] = "stalled"
            results.append(item)
            continue

        months_needed = remaining / monthly_pace
        if months_needed > 1200:
            item["status"] = "too_slow"
            results.append(item)
            continue

        projected = today + timedelta(days=round(months_needed * 30.44))
        item["months_needed"] = round(months_needed, 1)
        item["projected_date"] = projected

        if g.target_date is None:
            item["status"] = "projected"
        elif projected <= g.target_date:
            item["status"] = "on_track"
        else:
            item["status"] = "behind"
            days_left = (g.target_date - today).days
            if days_left > 0:
                needed = remaining / (days_left / 30.44)
                item["needed_per_month"] = round(needed, 2)
                item["extra_needed_per_month"] = round(needed - monthly_pace, 2)

        results.append(item)

    return results