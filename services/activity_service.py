"""Service layer for farm diary / activities."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.activity import FarmActivity
from models.crop import Crop
from schemas.activity import ActivityCreate, ActivityUpdate
from core.exceptions import NotFoundError, ValidationError
from core.auth import verify_farmer_ownership


class ActivityService:

    @staticmethod
    def create_activity(
        db: Session,
        farmer_id: str,
        activity_in: Optional[ActivityCreate] = None,
        activity_data: Optional[ActivityCreate] = None,
        **kwargs,
    ) -> FarmActivity:
        """Record a new farm activity. If crop_id is provided, verify farmer owns the crop."""
        effective_in = activity_in or activity_data or kwargs.get("activity_data")
        if not effective_in:
            raise ValidationError("Missing activity creation data.")

        if effective_in.crop_id:
            crop = db.query(Crop).filter(Crop.id == effective_in.crop_id).first()
            if not crop:
                raise NotFoundError(f"Linked crop {effective_in.crop_id} not found.")
            verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")

        desc = effective_in.description.strip() if effective_in.description else f"{effective_in.activity_type} activity"

        activity = FarmActivity(
            farmer_id=farmer_id,
            crop_id=effective_in.crop_id,
            activity_type=effective_in.activity_type.strip(),
            activity_date=effective_in.activity_date,
            description=desc,
            quantity=effective_in.quantity,
            unit=effective_in.unit.strip() if effective_in.unit else None,
            product_name=effective_in.product_name.strip() if effective_in.product_name else None,
            notes=effective_in.notes.strip() if effective_in.notes else None,
            cost=float(effective_in.cost) if effective_in.cost is not None else None,
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def get_activity(db: Session, farmer_id: str, activity_id: str) -> FarmActivity:
        """Get a single activity with ownership check."""
        activity = db.query(FarmActivity).filter(FarmActivity.id == activity_id).first()
        if not activity:
            raise NotFoundError(f"Activity {activity_id} not found.")
        verify_farmer_ownership(farmer_id, activity.farmer_id, resource_name="Activity")
        return activity

    @staticmethod
    def list_activities(
        db: Session,
        farmer_id: str,
        crop_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[FarmActivity]:
        """List activities owned by this farmer."""
        query = db.query(FarmActivity).filter(FarmActivity.farmer_id == farmer_id)
        if crop_id:
            query = query.filter(FarmActivity.crop_id == crop_id)
        if activity_type and activity_type != "all":
            query = query.filter(FarmActivity.activity_type == activity_type)
        return query.order_by(desc(FarmActivity.activity_date), desc(FarmActivity.created_at)).limit(limit).all()

    @staticmethod
    def update_activity(db: Session, farmer_id: str, activity_id: str, activity_in: ActivityUpdate) -> FarmActivity:
        """Update an activity with ownership check."""
        activity = ActivityService.get_activity(db, farmer_id, activity_id)

        update_data = activity_in.model_dump(exclude_unset=True)
        if "crop_id" in update_data and update_data["crop_id"]:
            crop = db.query(Crop).filter(Crop.id == update_data["crop_id"]).first()
            if not crop:
                raise NotFoundError(f"Linked crop {update_data['crop_id']} not found.")
            verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")

        for field, value in update_data.items():
            if value is not None and isinstance(value, str):
                value = value.strip()
            setattr(activity, field, value)

        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def delete_activity(db: Session, farmer_id: str, activity_id: str) -> bool:
        """Delete an activity with ownership verification."""
        activity = ActivityService.get_activity(db, farmer_id, activity_id)
        db.delete(activity)
        db.commit()
        return True
