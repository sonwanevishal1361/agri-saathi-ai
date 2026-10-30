"""Tests for Farm Expenses and Financial summary calculations."""

import pytest
from datetime import date
from schemas.expense import ExpenseCreate
from services.expense_service import ExpenseService


def test_expense_creation_and_validation(db_session, farmer_a, crop_farmer_a):
    exp = ExpenseService.create_expense(
        db_session,
        farmer_a.id,
        ExpenseCreate(
            crop_id=crop_farmer_a.id,
            category="Seeds",
            amount=2400.0,
            expense_date=date.today(),
            description="Purchased 2 packets Bt cotton seed",
            vendor="Mahabeej Kendra",
        ),
    )
    assert exp.id is not None
    assert exp.amount == 2400.0
    assert exp.category == "Seeds"
    assert exp.description == "Purchased 2 packets Bt cotton seed"


def test_invalid_expense_amount_rejected():
    with pytest.raises(ValueError):
        ExpenseCreate(category="Labor", amount=-100.0, expense_date=date.today(), description="Labor payment")


def test_expense_summary_calculations(db_session, farmer_a, crop_farmer_a):
    ExpenseService.create_expense(
        db_session,
        farmer_a.id,
        ExpenseCreate(crop_id=crop_farmer_a.id, category="Seeds", amount=2000.0, expense_date=date.today(), description="Seeds expense"),
    )
    ExpenseService.create_expense(
        db_session,
        farmer_a.id,
        ExpenseCreate(crop_id=crop_farmer_a.id, category="Fertilizers", amount=3500.0, expense_date=date.today(), description="Fertilizers expense"),
    )
    ExpenseService.create_expense(
        db_session,
        farmer_a.id,
        ExpenseCreate(crop_id=crop_farmer_a.id, category="Labor", amount=1500.0, expense_date=date.today(), description="Labor expense"),
    )

    summary = ExpenseService.get_expense_summary(db_session, farmer_a.id)
    assert summary["total_expenses"] == 7000.0
    assert summary["by_category"]["Seeds"] == 2000.0
    assert summary["by_category"]["Fertilizers"] == 3500.0
    assert summary["by_category"]["Labor"] == 1500.0


def test_list_expenses_with_limit(db_session, farmer_a, crop_farmer_a):
    for i in range(5):
        ExpenseService.create_expense(
            db_session,
            farmer_a.id,
            ExpenseCreate(
                crop_id=crop_farmer_a.id,
                category="Labor",
                amount=500.0 + i,
                expense_date=date.today(),
                description=f"Labor {i}",
            ),
        )

    all_exps = ExpenseService.list_expenses(db_session, farmer_a.id, limit=3)
    assert len(all_exps) == 3
