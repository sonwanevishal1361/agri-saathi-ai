"""Authentication and Farmer registration UI page."""

import streamlit as st
from core.database import get_db
from schemas.user import UserRegister, UserLogin
from services.user_service import UserService
from core.exceptions import AuthenticationError, DuplicateRecordError, ValidationError
from core.auth import AuthenticatedFarmer
from services.admin_service import AdminService
from ui.state import set_current_farmer, get_language, set_language, set_page
from utils.language import t


def render_auth_page():
    """Render Login and Registration tabs for farmers."""
    lang = get_language()

    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #1b5e20; margin-bottom: 5px;">🌱 AgriSaathi AI</h1>
            <h3 style="color: #2e7d32; font-weight: 500; margin-top: 0;">शेतकऱ्यांचा विश्वासू डिजिटल साथीदार | Your Smart Farming Companion</h3>
            <p style="color: #1b5e20; font-size: 0.9rem; font-weight: 600; margin: 4px 0 10px 0;">
                Platform Architect & Creator: <span style="background: #e8f5e9; padding: 4px 12px; border-radius: 14px; border: 1px solid #81c784;">Vishal Sonwane</span>
            </p>
            <p style="color: #555; font-size: 0.95rem;">Empowering Indian farmers with local crop guidance, weather, mandi prices, and smart farm management.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Language selector header
    col_lang1, col_lang2, col_lang3 = st.columns([1, 2, 1])
    with col_lang2:
        lang_choice = st.selectbox(
            "🌐 Choose Language / भाषा निवडा / भाषा चुनें",
            options=["mr", "hi", "en"],
            format_func=lambda x: "मराठी (Marathi)" if x == "mr" else ("हिंदी (Hindi)" if x == "hi" else "English"),
            index=0 if lang == "mr" else (1 if lang == "hi" else 2),
            key="auth_lang_select",
        )
        if lang_choice != lang:
            set_language(lang_choice)
            st.rerun()

    tab_login, tab_register, tab_admin = st.tabs([
        f"🔑 {t('login', lang)}",
        f"📝 {t('register', lang)}",
        "🛠️ ॲडमिन (Admin Login)",
    ])

    # ---------------- LOGIN TAB ----------------
    with tab_login:
        st.subheader(t("login", lang))
        with st.form("login_form", clear_on_submit=False):
            identifier = st.text_input(
                f"📱 {t('phone', lang)} / ✉️ {t('email', lang)}",
                placeholder="e.g. 9876543210 or farmer@example.com",
            )
            password = st.text_input(
                f"🔒 {t('password', lang)}",
                type="password",
                placeholder="Enter your password",
            )
            submitted = st.form_submit_button(f"🚀 {t('login', lang)}", use_container_width=True)

            if submitted:
                if not identifier or not password:
                    st.error("Please enter both login identifier and password.")
                else:
                    try:
                        with get_db() as db:
                            user = UserService.authenticate_farmer(
                                db,
                                UserLogin(identifier=identifier, password=password),
                            )
                            auth_farmer = AuthenticatedFarmer(
                                id=user.id,
                                full_name=user.full_name,
                                email=user.email,
                                phone=user.phone,
                                preferred_language=user.preferred_language or lang,
                                state=user.state,
                                district=user.district,
                                village=user.village,
                                is_active=user.is_active,
                                role=getattr(user, "role", "farmer") or "farmer",
                            )
                            set_current_farmer(auth_farmer)
                            st.success(f"Welcome back, {user.full_name}! 👋")
                            st.rerun()
                    except AuthenticationError as e:
                        st.error(f"❌ {e.message}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")

    # ---------------- REGISTER TAB ----------------
    with tab_register:
        st.subheader(t("register", lang))
        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input(f"👤 {t('full_name', lang)} *", placeholder="e.g. Ramesh Patil")
            c1, c2 = st.columns(2)
            with c1:
                phone = st.text_input(f"📱 {t('phone', lang)} *", placeholder="10-digit mobile number")
            with c2:
                email = st.text_input(f"✉️ {t('email', lang)} (Optional)", placeholder="farmer@example.com")

            p1, p2 = st.columns(2)
            with p1:
                new_password = st.text_input(f"🔒 {t('password', lang)} *", type="password", placeholder="At least 6 characters")
            with p2:
                confirm_password = st.text_input(f"🔒 {t('confirm_password', lang)} *", type="password", placeholder="Repeat password")

            st.markdown("##### 🌾 " + ("शेतीची माहिती (Farm Details)" if lang == "mr" else "Farm Details"))
            loc1, loc2, loc3 = st.columns(3)
            with loc1:
                state = st.selectbox(
                    f"📍 {t('state', lang)}",
                    options=["Maharashtra", "Punjab", "Madhya Pradesh", "Gujarat", "Karnataka", "Uttar Pradesh", "Telangana", "Andhra Pradesh", "Rajasthan", "Haryana", "Bihar", "West Bengal", "Tamil Nadu"],
                    index=0,
                )
            with loc2:
                district = st.text_input(f"🏙️ {t('district', lang)}", placeholder="e.g. Pune, Nashik, Nagpur")
            with loc3:
                village = st.text_input(f"🏡 {t('village', lang)}", placeholder="e.g. Baramati")

            farm1, farm2, farm3 = st.columns(3)
            with farm1:
                farm_size = st.number_input(f"📐 {t('farm_size', lang)}", min_value=0.0, max_value=500.0, value=2.0, step=0.5)
            with farm2:
                soil_type = st.selectbox(
                    f"🌱 {t('soil_type', lang)}",
                    options=["Black Clay (काळी माती)", "Red Loam (तांबडी माती)", "Alluvial (गाळाची माती)", "Sandy Loam (वाळूमिश्रित)", "Laterite (जांभा)"],
                )
            with farm3:
                irrigation = st.selectbox(
                    f"💧 {t('irrigation_method', lang)}",
                    options=["Drip Irrigation (ठिबक)", "Sprinkler (तुषार)", "Flood / Canal (पाटपाणी)", "Borewell / Well", "Rainfed (कोरडवाहू)"],
                )

            reg_submitted = st.form_submit_button(f"✅ {t('register', lang)}", use_container_width=True)

            if reg_submitted:
                try:
                    with get_db() as db:
                        reg_payload = UserRegister(
                            full_name=full_name,
                            phone=phone or None,
                            email=email or None,
                            password=new_password,
                            confirm_password=confirm_password,
                            preferred_language=lang,
                            state=state,
                            district=district or None,
                            village=village or None,
                            farm_size=farm_size,
                            farm_area_unit="Acre",
                            soil_type=soil_type,
                            irrigation_method=irrigation,
                        )
                        new_user = UserService.register_farmer(db, reg_payload)
                        auth_farmer = AuthenticatedFarmer(
                            id=new_user.id,
                            full_name=new_user.full_name,
                            email=new_user.email,
                            phone=new_user.phone,
                            preferred_language=new_user.preferred_language,
                            state=new_user.state,
                            district=new_user.district,
                            village=new_user.village,
                            is_active=new_user.is_active,
                            role=getattr(new_user, "role", "farmer") or "farmer",
                        )
                        set_current_farmer(auth_farmer)
                        st.success(f"Account registered successfully! Welcome to AgriSaathi AI, {new_user.full_name}!")
                        st.rerun()
                except (ValidationError, DuplicateRecordError) as e:
                    st.error(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")

    # ---------------- DEVELOPER / ADMIN PORTAL TAB ----------------
    with tab_admin:
        st.subheader("🛠️ Developer & Administrator Portal")
        st.caption("Secure role-based access for platform owner, developers, and system administrators.")
        with st.form("admin_login_form", clear_on_submit=False):
            admin_identifier = st.text_input(
                "👤 Admin Email / Phone",
                placeholder="e.g. admin@agrisaathi.com or 9999999999",
                key="admin_login_id",
            )
            admin_password = st.text_input(
                "🔒 Administrator Password",
                type="password",
                placeholder="Enter administrator password",
                key="admin_login_pw",
            )
            admin_submitted = st.form_submit_button("🚀 Authenticate Admin Access", use_container_width=True, type="primary")

            if admin_submitted:
                if not admin_identifier or not admin_password:
                    st.error("Please enter both admin identifier and password.")
                else:
                    try:
                        with get_db() as db:
                            admin_user = UserService.authenticate_farmer(
                                db,
                                UserLogin(identifier=admin_identifier, password=admin_password),
                            )
                            if getattr(admin_user, "role", "farmer") != "admin":
                                raise AuthenticationError("Access denied: This account does not possess administrator privileges.")

                            auth_admin = AuthenticatedFarmer(
                                id=admin_user.id,
                                full_name=admin_user.full_name,
                                email=admin_user.email,
                                phone=admin_user.phone,
                                preferred_language=admin_user.preferred_language or lang,
                                state=admin_user.state,
                                district=admin_user.district,
                                village=admin_user.village,
                                is_active=admin_user.is_active,
                                role="admin",
                            )
                            set_current_farmer(auth_admin)
                            set_page("admin")

                            # Log login audit trail
                            AdminService.log_action(
                                db=db,
                                admin=auth_admin,
                                action="LOGIN",
                                resource_type="system",
                                details={"portal": "admin_login_tab"},
                            )

                            st.success(f"Admin authentication verified! Welcome, {admin_user.full_name}.")
                            st.rerun()
                    except AuthenticationError as e:
                        st.error(f"❌ {e.message}")
                    except Exception as e:
                        st.error(f"Admin authentication error: {str(e)}")

