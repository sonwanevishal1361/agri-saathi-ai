"""Tests for farmer registration, password hashing, and authentication."""

import pytest
from schemas.user import UserRegister, UserLogin, PasswordChange
from services.user_service import UserService
from core.exceptions import AuthenticationError, DuplicateRecordError


def test_successful_registration(db_session):
    user = UserService.register_farmer(
        db_session,
        UserRegister(
            full_name="Santosh Gaikwad",
            phone="9876501234",
            email="santosh@example.com",
            password="SecurePassword@123",
            confirm_password="SecurePassword@123",
            preferred_language="mr",
        ),
    )
    assert user.id is not None
    assert user.full_name == "Santosh Gaikwad"
    # Verify password is not plaintext
    assert user.password_hash.startswith("$argon2id$")


def test_duplicate_phone_rejection(db_session, farmer_a):
    with pytest.raises(DuplicateRecordError):
        UserService.register_farmer(
            db_session,
            UserRegister(
                full_name="Duplicate Phone User",
                phone=farmer_a.phone,  # Same phone
                email="different@example.com",
                password="SecurePassword@123",
                confirm_password="SecurePassword@123",
            ),
        )


def test_duplicate_email_rejection(db_session, farmer_a):
    with pytest.raises(DuplicateRecordError):
        UserService.register_farmer(
            db_session,
            UserRegister(
                full_name="Duplicate Email User",
                phone="9899009988",
                email=farmer_a.email,  # Same email
                password="SecurePassword@123",
                confirm_password="SecurePassword@123",
            ),
        )


def test_password_mismatch_rejection():
    with pytest.raises(ValueError, match="Passwords do not match"):
        UserRegister(
            full_name="Mismatch User",
            phone="9812345678",
            password="Password123",
            confirm_password="DifferentPassword456",
        )


def test_successful_login(db_session, farmer_a):
    # Login via phone
    logged_in = UserService.authenticate_farmer(
        db_session,
        UserLogin(identifier=farmer_a.phone, password="StrongPassword123"),
    )
    assert logged_in.id == farmer_a.id

    # Login via email
    logged_in_email = UserService.authenticate_farmer(
        db_session,
        UserLogin(identifier=farmer_a.email, password="StrongPassword123"),
    )
    assert logged_in_email.id == farmer_a.id


def test_incorrect_password_rejection(db_session, farmer_a):
    with pytest.raises(AuthenticationError, match="Invalid password"):
        UserService.authenticate_farmer(
            db_session,
            UserLogin(identifier=farmer_a.phone, password="WrongPassword!"),
        )


def test_nonexistent_account_login(db_session):
    with pytest.raises(AuthenticationError, match="Farmer account not found"):
        UserService.authenticate_farmer(
            db_session,
            UserLogin(identifier="nonexistent@example.com", password="Password123"),
        )


def test_change_password(db_session, farmer_a):
    UserService.change_password(
        db_session,
        farmer_a.id,
        PasswordChange(
            old_password="StrongPassword123",
            new_password="NewStrongPassword456",
            confirm_new_password="NewStrongPassword456",
        ),
    )
    # Check old password no longer works
    with pytest.raises(AuthenticationError):
        UserService.authenticate_farmer(
            db_session,
            UserLogin(identifier=farmer_a.phone, password="StrongPassword123"),
        )
    # Check new password works
    user = UserService.authenticate_farmer(
        db_session,
        UserLogin(identifier=farmer_a.phone, password="NewStrongPassword456"),
    )
    assert user.id == farmer_a.id


def test_delete_account_cascade(db_session, farmer_a, crop_farmer_a):
    # Verify crop exists
    from models.crop import Crop
    crop = db_session.query(Crop).filter(Crop.id == crop_farmer_a.id).first()
    assert crop is not None

    # Delete farmer account
    UserService.delete_account(db_session, farmer_a.id, farmer_a.id)

    # Verify farmer and crop are removed (cascade)
    from models.user import User
    assert db_session.query(User).filter(User.id == farmer_a.id).first() is None
    assert db_session.query(Crop).filter(Crop.id == crop_farmer_a.id).first() is None
