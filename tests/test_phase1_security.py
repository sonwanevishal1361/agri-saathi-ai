"""Tests for Phase 1 Security Enhancements:
- Password policy validation
- Login attempt rate limiting and 15-minute lockout
- Initial admin provisioning with forced password change
- Per-user daily AI chat query rate limit and friendly localization
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from schemas.user import UserRegister, UserLogin
from services.user_service import UserService
from services.chat_service import ChatService
from scripts.create_admin import provision_admin
from core.security import validate_password_policy
from core.exceptions import AuthenticationError, ValidationError


def test_password_policy_validation():
    """Verify password policy enforces length, case, number, and special characters."""
    # Too short
    valid, msg = validate_password_policy("Ab1!")
    assert not valid
    assert "at least 8 characters" in msg

    # Missing uppercase
    valid, msg = validate_password_policy("lowercase123!@#")
    assert not valid
    assert "uppercase" in msg

    # Missing lowercase
    valid, msg = validate_password_policy("UPPERCASE123!@#")
    assert not valid
    assert "lowercase" in msg

    # Missing number
    valid, msg = validate_password_policy("NoDigitsHere!@#")
    assert not valid
    assert "digit" in msg

    # Missing special character
    valid, msg = validate_password_policy("NoSpecialChar1234")
    assert not valid
    assert "special character" in msg

    # Satisfies all rules
    valid, msg = validate_password_policy("Valid@Password2026")
    assert valid
    assert msg == ""


def test_login_rate_limiting_and_lockout(db_session):
    """Verify 5 failed login attempts lock account for 15 minutes and successful login resets counter."""
    user = UserService.register_farmer(
        db_session,
        UserRegister(
            full_name="Security Lockout Farmer",
            phone="9111222333",
            email="lockout@example.com",
            password="SecurePassword@123",
            confirm_password="SecurePassword@123",
            preferred_language="mr",
        ),
    )

    login_req_wrong = UserLogin(identifier=user.phone, password="WrongPassword!1")

    # First 4 failed attempts: account increments counter and warns remaining attempts
    for attempt in range(1, 5):
        with pytest.raises(AuthenticationError, match="attempts remaining"):
            UserService.authenticate_farmer(db_session, login_req_wrong)
        db_session.refresh(user)
        assert user.failed_login_attempts == attempt
        assert user.locked_until is None

    # 5th failed attempt: triggers lockout
    with pytest.raises(AuthenticationError, match="Account locked for 15 minutes"):
        UserService.authenticate_farmer(db_session, login_req_wrong)

    db_session.refresh(user)
    assert user.failed_login_attempts == 5
    assert user.locked_until is not None
    assert user.locked_until > datetime.now(timezone.utc).replace(tzinfo=None)

    # 6th attempt (even with right password while locked): rejected due to active lockout
    login_req_correct = UserLogin(identifier=user.phone, password="SecurePassword@123")
    with pytest.raises(AuthenticationError, match="temporarily locked"):
        UserService.authenticate_farmer(db_session, login_req_correct)

    # Fast-forward / expire the lockout window
    user.locked_until = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    db_session.commit()

    # Successful login: resets failed attempts and clears lockout
    authenticated = UserService.authenticate_farmer(db_session, login_req_correct)
    assert authenticated.id == user.id
    assert authenticated.failed_login_attempts == 0
    assert authenticated.locked_until is None


def test_admin_provisioning_and_forced_password_change(db_session):
    """Verify admin provisioning enforces must_change_password and password change clears it."""
    admin_email = "superadmin@example.local"
    temp_pass = "Initial@Pass123"

    admin = provision_admin(
        email=admin_email,
        password=temp_pass,
        full_name="Test Enterprise Admin",
        db=db_session,
    )

    assert admin.role == "admin"
    assert admin.must_change_password is True

    # Attempt to change with a weak password fails policy check
    with pytest.raises(ValidationError, match="at least 8 characters|uppercase|special"):
        UserService.change_password_forced(
            db=db_session,
            user_id=admin.id,
            current_password=temp_pass,
            new_password="weak",
        )

    # Attempt to change with wrong current password fails
    with pytest.raises(AuthenticationError, match="Current password is incorrect"):
        UserService.change_password_forced(
            db=db_session,
            user_id=admin.id,
            current_password="IncorrectPassword!",
            new_password="NewSecure@Password2026",
        )

    # Valid change updates password and clears must_change_password
    updated_admin = UserService.change_password_forced(
        db=db_session,
        user_id=admin.id,
        current_password=temp_pass,
        new_password="NewSecure@Password2026",
    )
    assert updated_admin.must_change_password is False

    # Authenticate with new password
    auth_user = UserService.authenticate_farmer(
        db_session,
        UserLogin(identifier=admin_email, password="NewSecure@Password2026"),
    )
    assert auth_user.id == admin.id


def test_ai_daily_limit_and_localization(db_session, farmer_a):
    """Verify daily AI request limit stops queries and returns friendly localized messages."""
    conv = ChatService.create_conversation(db_session, farmer_a.id, "Daily Limit Chat")

    # Localized messages exist for mr, hi, en
    msg_mr = ChatService.get_daily_limit_message("mr")
    msg_hi = ChatService.get_daily_limit_message("hi")
    msg_en = ChatService.get_daily_limit_message("en")

    assert "आजची AI प्रश्न मर्यादा पूर्ण झाली आहे" in msg_mr
    assert "1800-180-1551" in msg_mr
    assert "आज की AI प्रश्न सीमा पूरी हो गई है" in msg_hi
    assert "1800-180-1551" in msg_hi
    assert "Daily AI Question Limit Reached" in msg_en
    assert "1800-180-1551" in msg_en

    # Patch limit to 2 queries for testing
    with patch("services.chat_service.settings.AI_DAILY_REQUEST_LIMIT", 2):
        # Query 1
        with patch("services.chat_service.gemini_service.chat_completion", return_value="Response 1"):
            res1 = ChatService.send_message(db_session, farmer_a.id, conv.id, "Question 1", language="en")
            assert "Response 1" in res1["response"]

        # Query 2 (reaches limit)
        with patch("services.chat_service.gemini_service.chat_completion", return_value="Response 2"):
            res2 = ChatService.send_message(db_session, farmer_a.id, conv.id, "Question 2", language="en")
            assert "Response 2" in res2["response"]

        # Query 3 (exceeds limit - should return localized friendly limit notice without calling LLM)
        with patch("services.chat_service.gemini_service.chat_completion") as mock_llm:
            res3 = ChatService.send_message(db_session, farmer_a.id, conv.id, "Question 3", language="mr")
            assert "आजची AI प्रश्न मर्यादा पूर्ण झाली आहे" in res3["response"]
            mock_llm.assert_not_called()
