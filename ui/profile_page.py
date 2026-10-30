"""Farmer Profile and Account Settings UI page."""

import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.user_service import UserService
from schemas.user import UserUpdate, PasswordChange
from core.exceptions import ValidationError, AuthenticationError
from ui.state import set_language, logout, set_current_farmer


def render_profile_page(farmer: AuthenticatedFarmer):
    """Render profile details, settings, password change, and account deletion."""
    st.title("👤 शेतकरी प्रोफाइल व खाते सेटिंग्ज (Farmer Profile & Settings)")

    with get_db() as db:
        user_record = UserService.get_farmer_by_id(db, farmer.id)

    if not user_record:
        st.error("वापरकर्ता खाते सापडले नाही.")
        return

    tab_profile, tab_security, tab_danger = st.tabs([
        "📋 वैयक्तिक व शेती माहिती (Profile)",
        "🔒 पासवर्ड बदला (Security)",
        "⚠️ खाते हटवा (Delete Account)",
    ])

    # ---------------- TAB 1: PROFILE ----------------
    with tab_profile:
        with st.form("form_edit_profile"):
            st.markdown("##### 👤 मूलभूत माहिती (Basic Info)")
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("पूर्ण नाव (Full Name) *", value=user_record.full_name)
                phone_display = user_record.phone or "नोंदवलेला नाही"
                st.text_input("मोबाईल नंबर (Phone)", value=phone_display, disabled=True)
            with c2:
                email_display = user_record.email or "नोंदवलेला नाही"
                st.text_input("ईमेल (Email)", value=email_display, disabled=True)
                lang_sel = st.selectbox(
                    "🌐 मुख्य पसंतीची भाषा (Preferred Language)",
                    options=["mr", "hi", "en"],
                    format_func=lambda x: "मराठी (Marathi)" if x == "mr" else ("हिंदी (Hindi)" if x == "hi" else "English"),
                    index=0 if user_record.preferred_language == "mr" else (1 if user_record.preferred_language == "hi" else 2),
                )

            st.markdown("##### 🌾 शेतीचे ठिकाण व जमीन तपशील (Farm Location & Land)")
            l1, l2, l3 = st.columns(3)
            with l1:
                state = st.text_input("राज्य (State)", value=user_record.state or "Maharashtra")
            with l2:
                district = st.text_input("जिल्हा (District)", value=user_record.district or "")
            with l3:
                village = st.text_input("गाव (Village)", value=user_record.village or "")

            f1, f2, f3 = st.columns(3)
            with f1:
                farm_size = st.number_input("एकूण शेतजमीन (Acres)", min_value=0.0, value=float(user_record.farm_size or 2.0), step=0.5)
            with f2:
                soil_type = st.selectbox(
                    "मातीचा प्रकार (Soil)",
                    options=["Black Clay (काळी माती)", "Red Loam (तांबडी माती)", "Alluvial (गाळाची माती)", "Sandy Loam (वाळूमिश्रित)", "Medium Black (मध्यम काळी)"],
                    index=0,
                )
            with f3:
                irrigation = st.selectbox(
                    "मुख्य सिंचन (Irrigation)",
                    options=["Drip Irrigation (ठिबक)", "Sprinkler (तुषार)", "Flood / Canal (पाटपाणी)", "Borewell / Well", "Rainfed (कोरडवाहू)"],
                    index=0,
                )

            submitted = st.form_submit_button("✅ प्रोफाइल माहिती जतन करा (Save Changes)")

            if submitted:
                try:
                    with get_db() as db:
                        updated_user = UserService.update_profile(
                            db,
                            farmer.id,
                            UserUpdate(
                                full_name=name,
                                preferred_language=lang_sel,
                                state=state,
                                district=district,
                                village=village,
                                farm_size=farm_size,
                                soil_type=soil_type,
                                irrigation_method=irrigation,
                            ),
                        )
                        farmer.full_name = updated_user.full_name
                        farmer.preferred_language = updated_user.preferred_language
                        farmer.state = updated_user.state
                        farmer.district = updated_user.district
                        farmer.village = updated_user.village
                        set_current_farmer(farmer)
                        set_language(lang_sel)
                    st.success("माहिती यशस्वीरीत्या अद्ययावत केली!")
                    st.rerun()
                except ValidationError as e:
                    st.error(f"⚠️ {str(e)}")

    # ---------------- TAB 2: PASSWORD CHANGE ----------------
    with tab_security:
        st.markdown("##### 🔒 पासवर्ड बदला (Change Password)")
        with st.form("form_change_pw", clear_on_submit=True):
            old_pw = st.text_input("सध्याचा पासवर्ड (Current Password) *", type="password")
            new_pw = st.text_input("नवीन पासवर्ड (New Password) *", type="password", help="किमान ६ अक्षरे असावीत")
            confirm_pw = st.text_input("नवीन पासवर्ड पुन्हा टाका (Confirm New Password) *", type="password")

            pw_submit = st.form_submit_button("🔑 पासवर्ड बदला")

            if pw_submit:
                try:
                    with get_db() as db:
                        UserService.change_password(
                            db,
                            farmer.id,
                            PasswordChange(old_password=old_pw, new_password=new_pw, confirm_new_password=confirm_pw),
                        )
                    st.success("पासवर्ड यशस्वीरीत्या बदलला गेला!")
                except (ValidationError, AuthenticationError) as e:
                    st.error(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error(f"त्रुटी: {str(e)}")

    # ---------------- TAB 3: DELETE ACCOUNT ----------------
    with tab_danger:
        st.markdown("##### ⚠️ खाते व सर्व शेती नोंदी कायमस्वरूपी हटवा (Delete Account)")
        st.warning(
            "सावधान: हे खाते हटवल्यास आपल्या सर्व पिकांची माहिती, दैनंदिनी नोंदी, खर्च, उत्पन्न आणि AI संवाद कायमचे नष्ट होतील. "
            "ही क्रिया पूर्ववत करता येत नाही."
        )

        with st.form("form_delete_acc"):
            confirm_text = st.text_input(
                "खात्री करण्यासाठी 'DELETE' टाईप करा (Type 'DELETE' to confirm):"
            )
            del_submitted = st.form_submit_button("🚨 माझे खाते कायमस्वरूपी हटवा")

            if del_submitted:
                if confirm_text.strip() == "DELETE":
                    with get_db() as db:
                        UserService.delete_account(db, farmer.id, farmer.id)
                    logout()
                    st.success("आपले खाते यशस्वीरीत्या हटवले गेले.")
                    st.rerun()
                else:
                    st.error("कृपया खात्री करण्यासाठी अचूक 'DELETE' टाईप करा.")
