"""Tests for Phase 4 Compliance and Safety:
- Kisan Call Centre (1800-180-1551) & Krishi Vigyan Kendra (KVK) advisory disclaimers
- DPDP Act 2023 farmer personal data export (JSON)
- Verification that exports exclude password hashes and secret tokens
"""

import json
from services.chat_service import append_safety_disclaimer_if_needed
from services.user_service import UserService


def test_ai_chat_safety_disclaimer_triggered():
    """Verify chemical/pesticide advice automatically appends KCC and KVK advisory."""
    advice_en = "Apply 2 ml of chlorpyrifos 20 EC per litre of water to control bollworm."
    result_en = append_safety_disclaimer_if_needed(advice_en, language="en")
    assert "1800-180-1551" in result_en
    assert "Krishi Vigyan Kendra" in result_en
    assert "Kisan Call Centre" in result_en

    # Marathi
    advice_mr = "कपाशीवरील गुलाबी बोंडअळीच्या नियंत्रणासाठी कीटकनाशकाची फवारणी करा."
    result_mr = append_safety_disclaimer_if_needed(advice_mr, language="mr")
    assert "1800-180-1551" in result_mr
    assert "कृषी विज्ञान केंद्र" in result_mr
    assert "किसान कॉल सेंटर" in result_mr

    # Hindi
    advice_hi = "फसल में झुलसा रोग और फफूंद से बचाव के लिए फफूंदनाशक दवा का छिड़काव करें।"
    result_hi = append_safety_disclaimer_if_needed(advice_hi, language="hi")
    assert "1800-180-1551" in result_hi
    assert "कृषि विज्ञान केंद्र" in result_hi
    assert "किसान कॉल सेंटर" in result_hi


def test_ai_chat_safety_disclaimer_not_triggered_for_generic_query():
    """Verify generic farming queries without chemicals/diseases do not append unwanted disclaimers."""
    generic_text = "Today the weather in Pune is sunny with mild humidity."
    res = append_safety_disclaimer_if_needed(generic_text, language="en")
    assert res == generic_text
    assert "1800-180-1551" not in res


def test_ai_chat_safety_disclaimer_no_duplication():
    """Verify disclaimer is not duplicated if already included."""
    text_with_kcc = "For emergencies call Kisan Call Centre toll-free at 1800-180-1551 regarding pesticides."
    res = append_safety_disclaimer_if_needed(text_with_kcc, language="en")
    assert res == text_with_kcc
    assert res.count("1800-180-1551") == 1


def test_dpdp_export_farmer_personal_data(db_session, farmer_a):
    """Verify DPDP Act 2023 data export produces valid sanitized JSON containing farmer records."""
    data = UserService.export_farmer_personal_data(db_session, farmer_a.id)

    assert data["export_metadata"]["compliance"] == "Digital Personal Data Protection (DPDP) Act 2023"
    assert data["profile"]["full_name"] == farmer_a.full_name
    assert "crops" in data
    assert "activities" in data
    assert "expenses" in data
    assert "harvest_records" in data
    assert "ai_consultations" in data

    # Verify JSON serializability
    json_str = json.dumps(data)
    assert json_str is not None

    # CRITICAL: Verify NO sensitive password hashes or secret tokens exist in the exported payload
    assert "password_hash" not in json_str
    assert "argon2" not in json_str
    assert "secret" not in json_str.lower()

