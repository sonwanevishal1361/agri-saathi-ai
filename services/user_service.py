"""User and Farmer account service handling registration, login, and profile management."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import User
from schemas.user import UserRegister, UserLogin, UserUpdate, PasswordChange
from core.security import hash_password, verify_password, validate_password_strength
from core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DuplicateRecordError,
    NotFoundError,
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

        if not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("Invalid password. Please check and try again.")

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
    def seed_admin_if_missing(db: Session) -> Optional[User]:
        """Ensure at least one administrator account exists in the database."""
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            return admin

        from config import settings
        admin_email = settings.ADMIN_DEFAULT_EMAIL.strip().lower()
        admin_phone = settings.ADMIN_DEFAULT_PHONE.strip()
        admin_pass = settings.ADMIN_DEFAULT_PASSWORD

        # Check if user with that email or phone exists
        existing = db.query(User).filter(
            or_(User.email == admin_email, User.phone == admin_phone)
        ).first()

        if existing:
            existing.role = "admin"
            db.commit()
            logger.info(f"Promoted existing user {existing.id} to admin role.")
            return existing

        hashed = hash_password(admin_pass)
        admin_user = User(
            full_name="Platform Developer Admin (Vishal Sonwane)",
            email=admin_email,
            phone=admin_phone,
            password_hash=hashed,
            preferred_language="en",
            state="Maharashtra",
            district="Pune",
            village="Headquarters",
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"Seeded default developer admin account: {admin_user.email} (ID: {admin_user.id})")
        return admin_user
