"""User and Farmer account service handling registration, login, and profile management."""

from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from config import settings
from models.user import User
from schemas.user import UserRegister, UserLogin, UserUpdate, PasswordChange
from core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    validate_password_policy,
)
from core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DuplicateRecordError,
    NotFoundError,
    ValidationError,
)
from utils.logging_config import logger


class UserService:

    @staticmethod
    def register_farmer(db: Session, reg_data: UserRegister) -> User:
        """Register a new farmer account with hashed password."""
        # Check for existing email
        if reg_data.email:
            existing_email = db.query(User).filter(User.email == reg_data.email.strip().lower()).first()
            if existing_email:
                raise DuplicateRecordError("An account with this email address already exists.")

        # Check for existing phone
        if reg_data.phone:
            existing_phone = db.query(User).filter(User.phone == reg_data.phone.strip()).first()
            if existing_phone:
                raise DuplicateRecordError("An account with this phone number already exists.")

        validate_password_strength(reg_data.password)
        hashed = hash_password(reg_data.password)

        user = User(
            full_name=reg_data.full_name.strip(),
            email=reg_data.email.strip().lower() if reg_data.email else None,
            phone=reg_data.phone.strip() if reg_data.phone else None,
            password_hash=hashed,
            preferred_language=reg_data.preferred_language or "en",
            state=reg_data.state.strip() if reg_data.state else None,
            district=reg_data.district.strip() if reg_data.district else None,
            village=reg_data.village.strip() if reg_data.village else None,
            farm_size=reg_data.farm_size,
            farm_area_unit=reg_data.farm_area_unit or "Acre",
            soil_type=reg_data.soil_type.strip() if reg_data.soil_type else None,
            irrigation_method=reg_data.irrigation_method.strip() if reg_data.irrigation_method else None,
            role="farmer",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Registered new farmer account: {user.full_name} ({user.id})")
        return user

    @staticmethod
    def authenticate_farmer(db: Session, login_data: UserLogin) -> User:
        """Authenticate a farmer by email or phone and verify password."""
        identifier = login_data.identifier.strip().lower()
        if not identifier:
            raise AuthenticationError("Please enter your email or phone number.")

        user = db.query(User).filter(
            or_(
                User.email == identifier,
                User.phone == identifier,
            )
        ).first()

        if not user:
            raise AuthenticationError("Invalid login credentials. Farmer account not found.")

        if not user.is_active:
            raise AuthenticationError("This account is currently deactivated.")

        # Account Lockout Check
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if user.locked_until and user.locked_until > now:
            remaining_mins = max(1, int((user.locked_until - now).total_seconds() // 60) + 1)
            raise AuthenticationError(
                f"Account is temporarily locked due to multiple failed login attempts. Please try again after {remaining_mins} minutes."
            )

        if not verify_password(login_data.password, user.password_hash):
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
                db.commit()
                raise AuthenticationError(
                    f"Account locked for {settings.LOGIN_LOCKOUT_MINUTES} minutes due to {settings.MAX_FAILED_LOGIN_ATTEMPTS} consecutive failed login attempts."
                )
            db.commit()
            remaining = settings.MAX_FAILED_LOGIN_ATTEMPTS - user.failed_login_attempts
            raise AuthenticationError(
                f"Invalid password. Please check and try again. ({remaining} attempts remaining before temporary lockout)"
            )

        # Successful login: reset failed attempts & lockout window
        if (user.failed_login_attempts or 0) > 0 or user.locked_until is not None:
            user.failed_login_attempts = 0
            user.locked_until = None
            db.commit()

        logger.info(f"Farmer logged in successfully: {user.full_name} ({user.id})")
        return user

    @staticmethod
    def get_farmer_by_id(db: Session, farmer_id: str) -> Optional[User]:
        """Fetch farmer by user ID."""
        return db.query(User).filter(User.id == farmer_id).first()

    @staticmethod
    def update_profile(db: Session, farmer_id: str, update_data: UserUpdate) -> User:
        """Update farmer profile details."""
        user = db.query(User).filter(User.id == farmer_id).first()
        if not user:
            raise NotFoundError("Farmer account not found.")

        if update_data.full_name is not None:
            user.full_name = update_data.full_name.strip()
        if update_data.preferred_language is not None:
            user.preferred_language = update_data.preferred_language.strip()
        if update_data.state is not None:
            user.state = update_data.state.strip()
        if update_data.district is not None:
            user.district = update_data.district.strip()
        if update_data.village is not None:
            user.village = update_data.village.strip()
        if update_data.farm_size is not None:
            user.farm_size = update_data.farm_size
        if update_data.farm_area_unit is not None:
            user.farm_area_unit = update_data.farm_area_unit.strip()
        if update_data.soil_type is not None:
            user.soil_type = update_data.soil_type.strip()
        if update_data.irrigation_method is not None:
            user.irrigation_method = update_data.irrigation_method.strip()

        db.commit()
        db.refresh(user)
        logger.info(f"Updated profile for farmer: {user.id}")
        return user

    @staticmethod
    def change_password(db: Session, farmer_id: str, pw_data: PasswordChange) -> None:
        """Change farmer password after verifying old password."""
        user = db.query(User).filter(User.id == farmer_id).first()
        if not user:
            raise NotFoundError("Farmer account not found.")

        if not verify_password(pw_data.old_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect.")

        validate_password_strength(pw_data.new_password)
        user.password_hash = hash_password(pw_data.new_password)
        db.commit()
        logger.info(f"Password changed for farmer: {user.id}")

    @staticmethod
    def delete_account(db: Session, farmer_id: str, confirm_farmer_id: str) -> None:
        """Permanently delete farmer account and cascade delete all associated data."""
        if str(farmer_id) != str(confirm_farmer_id):
            raise AuthorizationError("Cannot delete account: Identity mismatch.")

        user = db.query(User).filter(User.id == farmer_id).first()
        if not user:
            raise NotFoundError("Farmer account not found.")

        db.delete(user)
        db.commit()
        logger.warning(f"Farmer account deleted permanently: {farmer_id}")

    @staticmethod
    def export_farmer_personal_data(db: Session, farmer_id: str) -> dict:
        """Export complete personal dataset for authenticated farmer under DPDP Act 2023."""
        user = db.query(User).filter(User.id == farmer_id).first()
        if not user:
            raise NotFoundError("Farmer account not found.")

        from models.crop import Crop
        from models.activity import FarmActivity
        from models.expense import Expense
        from models.harvest import HarvestRecord
        from models.conversation import Conversation, Message

        crops = db.query(Crop).filter(Crop.farmer_id == farmer_id).all()
        activities = db.query(FarmActivity).filter(FarmActivity.farmer_id == farmer_id).all()
        expenses = db.query(Expense).filter(Expense.farmer_id == farmer_id).all()
        harvests = db.query(HarvestRecord).filter(HarvestRecord.farmer_id == farmer_id).all()
        conversations = db.query(Conversation).filter(Conversation.farmer_id == farmer_id).all()

        conv_data = []
        for c in conversations:
            msgs = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.asc()).all()
            conv_data.append({
                "conversation_id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "messages": [
                    {
                        "role": m.role,
                        "content": m.content,
                        "timestamp": m.created_at.isoformat() if m.created_at else None,
                    }
                    for m in msgs
                ],
            })

        return {
            "export_metadata": {
                "system": "AgriSaathi AI",
                "compliance": "Digital Personal Data Protection (DPDP) Act 2023",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "farmer_id": user.id,
            },
            "profile": {
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "state": user.state,
                "district": user.district,
                "village": user.village,
                "farm_size": user.farm_size,
                "farm_area_unit": user.farm_area_unit,
                "soil_type": user.soil_type,
                "irrigation_method": user.irrigation_method,
                "preferred_language": user.preferred_language,
                "registered_at": user.created_at.isoformat() if user.created_at else None,
            },
            "crops": [
                {
                    "id": cr.id,
                    "name": cr.name,
                    "variety": cr.variety,
                    "area": cr.area,
                    "area_unit": cr.area_unit,
                    "sowing_date": str(cr.sowing_date) if cr.sowing_date else None,
                    "expected_harvest_date": str(cr.expected_harvest_date) if cr.expected_harvest_date else None,
                    "growth_stage": cr.growth_stage,
                    "status": cr.status,
                }
                for cr in crops
            ],
            "activities": [
                {
                    "id": a.id,
                    "crop_id": a.crop_id,
                    "activity_type": a.activity_type,
                    "title": a.title,
                    "description": a.description,
                    "activity_date": str(a.activity_date) if a.activity_date else None,
                    "cost": a.cost,
                }
                for a in activities
            ],
            "expenses": [
                {
                    "id": e.id,
                    "crop_id": e.crop_id,
                    "category": e.category,
                    "title": e.title,
                    "amount": e.amount,
                    "expense_date": str(e.expense_date) if e.expense_date else None,
                    "payment_mode": e.payment_mode,
                }
                for e in expenses
            ],
            "harvest_records": [
                {
                    "id": h.id,
                    "crop_id": h.crop_id,
                    "quantity": h.quantity,
                    "quantity_unit": h.quantity_unit,
                    "selling_price": h.selling_price,
                    "total_revenue": h.total_revenue,
                    "harvest_date": str(h.harvest_date) if h.harvest_date else None,
                }
                for h in harvests
            ],
            "ai_consultations": conv_data,
        }

    @staticmethod
    def change_password_forced(
        db: Session,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> User:
        """Force user to change temporary/initial password enforcing strict password policy."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User account not found.")

        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect.")

        is_valid, err_msg = validate_password_policy(new_password)
        if not is_valid:
            raise ValidationError(err_msg)

        user.password_hash = hash_password(new_password)
        user.must_change_password = False
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()
        db.refresh(user)
        logger.info(f"Forced password change completed for user: {user.id}")
        return user

    @staticmethod
    def seed_admin_if_missing(db: Session) -> Optional[User]:
        """Ensure the primary platform administrator account exists and is ready for login.

        Guarantees that `sonwanevishal1361@gmail.com` (or environment-configured ADMIN_EMAIL)
        is provisioned with the administrator role, active status, unblocked login, and valid password hash.
        """
        admin_email = (settings.ADMIN_EMAIL or "sonwanevishal1361@gmail.com").strip().lower()
        admin_pass = (settings.ADMIN_PASSWORD or "vishal1361").strip()
        admin_phone = (settings.ADMIN_PHONE or "1234567890").strip()
        admin_name = getattr(settings, "ADMIN_NAME", "Vishal Sonwane") or "Vishal Sonwane"

        # Check if user with that email or phone exists
        conditions = [User.email == admin_email]
        if admin_phone:
            conditions.append(User.phone == admin_phone)
        existing = db.query(User).filter(or_(*conditions)).first()

        if existing:
            needs_commit = False
            if existing.role != "admin":
                existing.role = "admin"
                needs_commit = True
            if existing.must_change_password:
                existing.must_change_password = False
                needs_commit = True
            if not existing.is_active:
                existing.is_active = True
                needs_commit = True
            if existing.failed_login_attempts or existing.locked_until:
                existing.failed_login_attempts = 0
                existing.locked_until = None
                needs_commit = True
            if not verify_password(admin_pass, existing.password_hash):
                existing.password_hash = hash_password(admin_pass)
                needs_commit = True
            if not existing.full_name or existing.full_name in ("sa", "Platform Administrator", "AgriSaathi Administrator"):
                existing.full_name = admin_name
                needs_commit = True
            if not existing.email:
                existing.email = admin_email
                needs_commit = True
            if admin_phone and not existing.phone:
                existing.phone = admin_phone
                needs_commit = True

            if needs_commit:
                db.commit()
                db.refresh(existing)
            logger.info(f"Primary administrator account verified: {existing.email} ({existing.id})")
            return existing

        # Create new primary admin user
        hashed = hash_password(admin_pass)
        admin_user = User(
            full_name=admin_name,
            email=admin_email,
            phone=admin_phone or None,
            password_hash=hashed,
            preferred_language="en",
            state="Maharashtra",
            district="Pune",
            village="Headquarters",
            role="admin",
            must_change_password=False,
            is_active=True,
            failed_login_attempts=0,
            locked_until=None,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"Provisioned administrator account: {admin_user.email} (ID: {admin_user.id})")
        return admin_user
