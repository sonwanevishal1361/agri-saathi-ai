"""Service layer for farm expense tracking and financial calculations."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.expense import Expense
from models.crop import Crop
from schemas.expense import ExpenseCreate, ExpenseUpdate
from core.exceptions import NotFoundError, ValidationError
from core.auth import verify_farmer_ownership


class ExpenseService:

    @staticmethod
    def create_expense(
        db: Session,
        farmer_id: str,
        expense_in: Optional[ExpenseCreate] = None,
        expense_data: Optional[ExpenseCreate] = None,
        **kwargs,
    ) -> Expense:
        """Create a new expense entry."""
        effective_in = expense_in or expense_data or kwargs.get("expense_data")
        if not effective_in:
            raise ValidationError("Missing expense creation data.")

        if effective_in.amount < 0:
            raise ValidationError("Expense amount cannot be negative.")

        if effective_in.crop_id:
            crop = db.query(Crop).filter(Crop.id == effective_in.crop_id).first()
            if not crop:
                raise NotFoundError(f"Linked crop {effective_in.crop_id} not found.")
            verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")

        expense = Expense(
            farmer_id=farmer_id,
            crop_id=effective_in.crop_id,
            category=effective_in.category.strip(),
            amount=round(float(effective_in.amount), 2),
            currency=effective_in.currency.strip().upper(),
            expense_date=effective_in.expense_date,
            description=effective_in.description.strip(),
            vendor=effective_in.vendor.strip() if effective_in.vendor else None,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def get_expense(db: Session, farmer_id: str, expense_id: str) -> Expense:
        """Get an expense record with ownership check."""
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise NotFoundError(f"Expense {expense_id} not found.")
        verify_farmer_ownership(farmer_id, expense.farmer_id, resource_name="Expense")
        return expense

    @staticmethod
    def list_expenses(
        db: Session,
        farmer_id: str,
        crop_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Expense]:
        """List expenses owned by the farmer."""
        query = db.query(Expense).filter(Expense.farmer_id == farmer_id)
        if crop_id:
            query = query.filter(Expense.crop_id == crop_id)
        if category and category != "all":
            query = query.filter(Expense.category == category)
        query = query.order_by(desc(Expense.expense_date), desc(Expense.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def update_expense(db: Session, farmer_id: str, expense_id: str, expense_in: ExpenseUpdate) -> Expense:
        """Update an expense record."""
        expense = ExpenseService.get_expense(db, farmer_id, expense_id)
        update_data = expense_in.model_dump(exclude_unset=True)

        if "amount" in update_data and update_data["amount"] is not None:
            if update_data["amount"] < 0:
                raise ValidationError("Expense amount cannot be negative.")
            update_data["amount"] = round(float(update_data["amount"]), 2)

        if "crop_id" in update_data and update_data["crop_id"]:
            crop = db.query(Crop).filter(Crop.id == update_data["crop_id"]).first()
            if not crop:
                raise NotFoundError(f"Linked crop {update_data['crop_id']} not found.")
            verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")

        for field, value in update_data.items():
            if value is not None and isinstance(value, str):
                value = value.strip()
            setattr(expense, field, value)

        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def delete_expense(db: Session, farmer_id: str, expense_id: str) -> bool:
        """Delete an expense record."""
        expense = ExpenseService.get_expense(db, farmer_id, expense_id)
        db.delete(expense)
        db.commit()
        return True

    @staticmethod
    def get_expense_summary(db: Session, farmer_id: str, crop_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate total expenses and breakdown by category and crop."""
        query = db.query(Expense).filter(Expense.farmer_id == farmer_id)
        if crop_id:
            query = query.filter(Expense.crop_id == crop_id)

        expenses = query.all()
        total_amount = sum(e.amount for e in expenses)

        by_category: Dict[str, float] = {}
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, 0.0) + e.amount

        # By crop name
        by_crop: Dict[str, float] = {}
        for e in expenses:
            c_name = e.crop.name if e.crop else "General / Unassigned"
            by_crop[c_name] = by_crop.get(c_name, 0.0) + e.amount

        return {
            "total_expenses": round(total_amount, 2),
            "total_expense": round(total_amount, 2),
            "by_category": {k: round(v, 2) for k, v in by_category.items()},
            "by_crop": {k: round(v, 2) for k, v in by_crop.items()},
            "count": len(expenses),
        }
