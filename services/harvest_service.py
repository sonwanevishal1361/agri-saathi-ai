"""Service layer for harvest yields, sales, and net balance calculation."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.harvest import HarvestRecord
from models.crop import Crop
from models.expense import Expense
from schemas.harvest import HarvestCreate, HarvestUpdate
from core.exceptions import NotFoundError, ValidationError
from core.auth import verify_farmer_ownership


class HarvestService:

    @staticmethod
    def create_harvest(
        db: Session,
        farmer_id: str,
        harvest_in: Optional[HarvestCreate] = None,
        harvest_data: Optional[HarvestCreate] = None,
        **kwargs,
    ) -> HarvestRecord:
        """Create a harvest record. Verify crop ownership."""
        effective_in = harvest_in or harvest_data or kwargs.get("harvest_data")
        if not effective_in:
            raise ValidationError("Missing harvest creation data.")

        if effective_in.quantity <= 0:
            raise ValidationError("Harvested quantity must be greater than zero.")

        crop = db.query(Crop).filter(Crop.id == effective_in.crop_id).first()
        if not crop:
            raise NotFoundError(f"Linked crop {effective_in.crop_id} not found.")
        verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")

        if effective_in.sale_quantity is not None and effective_in.sale_quantity < 0:
            raise ValidationError("Sale quantity cannot be negative.")
        if effective_in.selling_price is not None and effective_in.selling_price < 0:
            raise ValidationError("Selling price cannot be negative.")

        harvest = HarvestRecord(
            farmer_id=farmer_id,
            crop_id=effective_in.crop_id,
            harvest_date=effective_in.harvest_date,
            quantity=float(effective_in.quantity),
            quantity_unit=effective_in.quantity_unit.strip(),
            sale_quantity=float(effective_in.sale_quantity) if effective_in.sale_quantity is not None else None,
            selling_price=float(effective_in.selling_price) if effective_in.selling_price is not None else None,
            notes=effective_in.notes.strip() if effective_in.notes else None,
        )
        db.add(harvest)
        db.commit()
        db.refresh(harvest)
        return harvest

    @staticmethod
    def get_harvest(db: Session, farmer_id: str, harvest_id: str) -> HarvestRecord:
        """Get a harvest record with ownership check."""
        harvest = db.query(HarvestRecord).filter(HarvestRecord.id == harvest_id).first()
        if not harvest:
            raise NotFoundError(f"Harvest record {harvest_id} not found.")
        verify_farmer_ownership(farmer_id, harvest.farmer_id, resource_name="Harvest Record")
        return harvest

    @staticmethod
    def list_harvests(
        db: Session,
        farmer_id: str,
        crop_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[HarvestRecord]:
        """List harvest records for the farmer."""
        query = db.query(HarvestRecord).filter(HarvestRecord.farmer_id == farmer_id)
        if crop_id:
            query = query.filter(HarvestRecord.crop_id == crop_id)
        query = query.order_by(desc(HarvestRecord.harvest_date), desc(HarvestRecord.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def update_harvest(db: Session, farmer_id: str, harvest_id: str, harvest_in: HarvestUpdate) -> HarvestRecord:
        """Update a harvest record."""
        harvest = HarvestService.get_harvest(db, farmer_id, harvest_id)
        update_data = harvest_in.model_dump(exclude_unset=True)

        if "quantity" in update_data and update_data["quantity"] is not None:
            if update_data["quantity"] <= 0:
                raise ValidationError("Harvested quantity must be greater than zero.")
        if "sale_quantity" in update_data and update_data["sale_quantity"] is not None:
            if update_data["sale_quantity"] < 0:
                raise ValidationError("Sale quantity cannot be negative.")
        if "selling_price" in update_data and update_data["selling_price"] is not None:
            if update_data["selling_price"] < 0:
                raise ValidationError("Selling price cannot be negative.")

        for field, value in update_data.items():
            if value is not None and isinstance(value, str):
                value = value.strip()
            setattr(harvest, field, value)

        db.commit()
        db.refresh(harvest)
        return harvest

    @staticmethod
    def delete_harvest(db: Session, farmer_id: str, harvest_id: str) -> bool:
        """Delete a harvest record."""
        harvest = HarvestService.get_harvest(db, farmer_id, harvest_id)
        db.delete(harvest)
        db.commit()
        return True

    @staticmethod
    def get_crop_financial_summary(db: Session, farmer_id: str, crop_id: str) -> Dict[str, Any]:
        """Calculate recorded sales revenue, expenses, and net balance for a specific crop."""
        crop = db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise NotFoundError(f"Crop {crop_id} not found.")
        verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")

        harvests = db.query(HarvestRecord).filter(HarvestRecord.crop_id == crop_id).all()
        expenses = db.query(Expense).filter(Expense.crop_id == crop_id).all()

        total_expenses = sum(e.amount for e in expenses)
        total_quantity = sum(h.quantity for h in harvests)

        # Revenue calculation: sale_quantity * selling_price (or direct selling_price if quantity not split)
        total_revenue = 0.0
        for h in harvests:
            if h.selling_price is not None:
                if h.sale_quantity is not None and h.sale_quantity > 0:
                    total_revenue += h.sale_quantity * h.selling_price
                else:
                    total_revenue += h.selling_price

        net_balance = total_revenue - total_expenses

        return {
            "crop_id": crop_id,
            "crop_name": crop.name,
            "total_harvest_quantity": round(total_quantity, 2),
            "total_expenses": round(total_expenses, 2),
            "total_revenue": round(total_revenue, 2),
            "net_profit": round(net_balance, 2),
            "net_balance": round(net_balance, 2),
            "has_sales_data": total_revenue > 0,
        }

    @staticmethod
    def get_harvest_summary(db: Session, farmer_id: str, crop_id: Optional[str] = None) -> Dict[str, Any]:
        """Farmer-wide or crop-specific harvest and profit summary."""
        if crop_id:
            return HarvestService.get_crop_financial_summary(db, farmer_id, crop_id)

        harvests = db.query(HarvestRecord).filter(HarvestRecord.farmer_id == farmer_id).all()
        expenses = db.query(Expense).filter(Expense.farmer_id == farmer_id).all()

        total_expenses = sum(e.amount for e in expenses)
        total_revenue = sum(h.total_revenue for h in harvests)
        total_quantity = sum(h.quantity for h in harvests)
        net_profit = total_revenue - total_expenses

        return {
            "total_harvest_quantity": round(total_quantity, 2),
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(net_profit, 2),
            "count": len(harvests),
        }

    # Backward-compatible convenience aliases
    create_harvest_record = create_harvest
    get_harvest_record = get_harvest
    list_harvest_records = list_harvests
    delete_harvest_record = delete_harvest
