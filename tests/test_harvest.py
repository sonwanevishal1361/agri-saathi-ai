"""Tests for Harvest records and Net Profit calculations."""

from datetime import date
from schemas.harvest import HarvestCreate
from schemas.expense import ExpenseCreate
from services.harvest_service import HarvestService
from services.expense_service import ExpenseService


def test_harvest_record_creation_and_revenue_calculation(db_session, farmer_a, crop_farmer_a):
    harv = HarvestService.create_harvest(
        db_session,
        farmer_a.id,
        HarvestCreate(
            crop_id=crop_farmer_a.id,
            harvest_date=date.today(),
            quantity=15.0,
            quantity_unit="Quintal",
            selling_price=7200.0,
            sale_quantity=15.0,
            notes="Sold at Baramati APMC",
        ),
    )
    assert harv.id is not None
    # 15 * 7200 = 108,000
    assert harv.total_revenue == 108000.0


def test_harvest_and_expense_net_profit_summary(db_session, farmer_a, crop_farmer_a):
    # Log 25,000 in expenses
    ExpenseService.create_expense(
        db_session,
        farmer_a.id,
        ExpenseCreate(crop_id=crop_farmer_a.id, category="Seeds", amount=5000.0, expense_date=date.today(), description="Seeds"),
    )
    ExpenseService.create_expense(
        db_session,
        farmer_a.id,
        ExpenseCreate(crop_id=crop_farmer_a.id, category="Fertilizers", amount=20000.0, expense_date=date.today(), description="Fertilizers"),
    )

    # Log 100,000 in harvest revenue
    HarvestService.create_harvest(
        db_session,
        farmer_a.id,
        HarvestCreate(
            crop_id=crop_farmer_a.id,
            harvest_date=date.today(),
            quantity=20.0,
            quantity_unit="Quintal",
            sale_quantity=20.0,
            selling_price=5000.0,
        ),
    )

    summary = HarvestService.get_harvest_summary(db_session, farmer_a.id)
    assert summary["total_revenue"] == 100000.0
    assert summary["total_expenses"] == 25000.0
    assert summary["net_profit"] == 75000.0
