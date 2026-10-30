"""Service layer for crop management with strict farmer data isolation."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.crop import Crop
from schemas.crop import CropCreate, CropUpdate
from core.exceptions import NotFoundError, ValidationError
from core.auth import verify_farmer_ownership


class CropService:

    @staticmethod
    def create_crop(
        db: Session,
        farmer_id: str,
        crop_in: Optional[CropCreate] = None,
        crop_data: Optional[CropCreate] = None,
        **kwargs,
    ) -> Crop:
        """Create a new crop record owned by the authenticated farmer."""
        effective_crop_in = crop_in or crop_data or kwargs.get("crop_data")
        if not effective_crop_in:
            raise ValidationError("Missing crop creation data.")
        if effective_crop_in.area <= 0:
            raise ValidationError("Crop area must be greater than zero.")

        crop = Crop(
            farmer_id=farmer_id,
            name=effective_crop_in.name.strip(),
            variety=effective_crop_in.variety.strip() if effective_crop_in.variety else None,
            plot_name=effective_crop_in.plot_name.strip() if effective_crop_in.plot_name else None,
            area=float(effective_crop_in.area),
            area_unit=effective_crop_in.area_unit,
            sowing_date=effective_crop_in.sowing_date,
            expected_harvest_date=effective_crop_in.expected_harvest_date,
            actual_harvest_date=effective_crop_in.actual_harvest_date,
            soil_type=effective_crop_in.soil_type.strip() if effective_crop_in.soil_type else None,
            irrigation_method=effective_crop_in.irrigation_method.strip() if effective_crop_in.irrigation_method else None,
            growth_stage=effective_crop_in.growth_stage,
            status=effective_crop_in.status,
            notes=effective_crop_in.notes.strip() if effective_crop_in.notes else None,
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        return crop

    @staticmethod
    def get_crop(db: Session, farmer_id: str, crop_id: str) -> Crop:
        """Get a single crop verifying farmer ownership."""
        crop = db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise NotFoundError(f"Crop with ID {crop_id} not found.")
        verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")
        return crop

    @staticmethod
    def list_crops(
        db: Session,
        farmer_id: str,
        status: Optional[str] = None,
        name_search: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Crop]:
        """List all crops belonging strictly to the authenticated farmer."""
        query = db.query(Crop).filter(Crop.farmer_id == farmer_id)
        if status and status != "all":
            query = query.filter(Crop.status == status)
        if name_search:
            query = query.filter(Crop.name.ilike(f"%{name_search.strip()}%"))
        query = query.order_by(desc(Crop.sowing_date))
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def update_crop(db: Session, farmer_id: str, crop_id: str, crop_in: CropUpdate) -> Crop:
        """Update an existing crop record with ownership enforcement."""
        crop = CropService.get_crop(db, farmer_id, crop_id)
        update_data = crop_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None and isinstance(value, str):
                value = value.strip()
            setattr(crop, field, value)

        db.commit()
        db.refresh(crop)
        return crop

    @staticmethod
    def delete_crop(db: Session, farmer_id: str, crop_id: str) -> bool:
        """Delete a crop record with ownership verification."""
        crop = CropService.get_crop(db, farmer_id, crop_id)
        db.delete(crop)
        db.commit()
        return True

    @staticmethod
    def count_active_crops(db: Session, farmer_id: str) -> int:
        """Count active crops for dashboard."""
        return db.query(Crop).filter(
            Crop.farmer_id == farmer_id,
            Crop.status == "active",
        ).count()
