"""Authentication and Farmer registration UI page.

Features an Apple-inspired, immersive agricultural split-screen layout with
one-click demo farmer testing, responsive mobile stacking, and DPDP Act 2023 compliance.
"""

import textwrap
import streamlit as st
from core.config import settings
from core.database import get_db
from schemas.user import UserRegister, UserLogin
from services.user_service import UserService
from core.exceptions import AuthenticationError, DuplicateRecordError, ValidationError
from core.auth import AuthenticatedFarmer
from services.admin_service import AdminService
from ui.state import set_current_farmer, get_language, set_language, set_page
from utils.language import t
from ui.components.icons import get_icon
from ui.theme import clean_html


def _perform_direct_login(identifier: str, password: str, lang: str):
    """Authenticate and directly set session state for instant 1-click access."""
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
                must_change_password=getattr(user, "must_change_password", False),
            )
            set_current_farmer(auth_farmer)
            st.success(f"Welcome, {user.full_name}! 👋")
            st.rerun()
    except AuthenticationError as e:
        st.error(f"❌ {e.message}")
    except Exception as e:
        st.error(f"Login error: {str(e)}")


def render_auth_page():
    """Render the split-screen authentication experience."""
    lang = get_language()

    # Split-screen responsive container
    col_visual, col_form = st.columns([5, 6], gap="large")

    # =========================================================================
    # LEFT PANE: IMMERSIVE AGRICULTURAL HERO SHOWCASE
    # =========================================================================
    with col_visual:
        sprout_svg = get_icon("sprout", size=32, color="#86efac", stroke_width=2.0)
        leaf_svg = get_icon("leaf", size=20, color="#86efac")
        chart_svg = get_icon("trending-up", size=20, color="#fde047")
        bot_svg = get_icon("bot", size=20, color="#93c5fd")
        shield_svg = get_icon("shield-check", size=18, color="#86efac")

        left_html = textwrap.dedent(f"""
            <div style="background: linear-gradient(145deg, #071e13 0%, #0b2f1e 45%, #14462c 80%, #1e5a39 100%); border-radius: 26px; padding: 36px 30px; color: #ffffff; box-shadow: 0 16px 40px -8px rgba(7, 30, 19, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15); border: 1px solid rgba(134, 239, 172, 0.2); position: relative; overflow: hidden; margin-bottom: 20px;">
                <div style="position: absolute; top: -60px; right: -60px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(134, 239, 172, 0.15) 0%, transparent 70%); border-radius: 50%; pointer-events: none;"></div>
                <div style="position: absolute; bottom: -80px; left: -60px; width: 260px; height: 260px; background: radial-gradient(circle, rgba(253, 224, 71, 0.1) 0%, transparent 70%); border-radius: 50%; pointer-events: none;"></div>
                <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px;">
                    <div style="width: 52px; height: 52px; border-radius: 16px; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px); flex-shrink: 0;">
                        {sprout_svg}
                    </div>
                    <div>
                        <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; color: #86efac; text-transform: uppercase;">Next-Gen Indian Agritech</div>
                        <h1 style="margin: 2px 0 0 0; color: #ffffff; font-size: 1.85rem; font-weight: 800; letter-spacing: -0.02em;">AgriSaathi AI</h1>
                    </div>
                </div>
                <p style="color: #d1fae5; font-size: 1.05rem; line-height: 1.55; margin: 0 0 24px 0; font-weight: 500;">
                    शेतकऱ्यांचा विश्वासू डिजिटल साथीदार — Empowering Maharashtra & Indian farmers with verified crop intelligence, live mandi logistics, and bilingual AI assistance.
                </p>
                <div style="display: flex; flex-direction: column; gap: 14px; margin-bottom: 28px;">
                    <div style="display: flex; align-items: flex-start; gap: 14px; background: rgba(255,255,255,0.06); padding: 12px 16px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="margin-top: 2px; flex-shrink: 0;">{leaf_svg}</div>
                        <div>
                            <div style="font-weight: 700; color: #ffffff; font-size: 0.98rem;">Smart 6-Stage Crop Tracker</div>
                            <div style="color: #a7f3d0; font-size: 0.88rem; line-height: 1.4; margin-top: 2px;">ICAR-backed growth stage monitoring for Cotton, Soybean, Wheat & Cash Crops.</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 14px; background: rgba(255,255,255,0.06); padding: 12px 16px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="margin-top: 2px; flex-shrink: 0;">{chart_svg}</div>
                        <div>
                            <div style="font-weight: 700; color: #ffffff; font-size: 0.98rem;">Live Mandi Net-Price Discovery</div>
                            <div style="color: #fef08a; font-size: 0.88rem; line-height: 1.4; margin-top: 2px;">Real-time APMC price comparison with automatic transport cost subtraction.</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 14px; background: rgba(255,255,255,0.06); padding: 12px 16px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="margin-top: 2px; flex-shrink: 0;">{bot_svg}</div>
                        <div>
                            <div style="font-weight: 700; color: #ffffff; font-size: 0.98rem;">Bilingual Voice AI Companion</div>
                            <div style="color: #bfdbfe; font-size: 0.88rem; line-height: 1.4; margin-top: 2px;">Marathi & Hindi conversational advisor with speech recognition & audio read-aloud.</div>
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 18px;">
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.84rem; color: #a7f3d0; font-weight: 600;">
                        {shield_svg} DPDP Act 2023 Compliant
                    </div>
                    <div style="font-size: 0.84rem; color: rgba(255,255,255,0.85); font-weight: 600;">
                        Architect: <strong>Vishal Sonwane</strong>
                    </div>
                </div>
            </div>
        """).strip()
        st.markdown(clean_html(left_html), unsafe_allow_html=True)

    # =========================================================================
    # RIGHT PANE: ELEGANT AUTHENTICATION FORMS & DEMO BUTTONS
    # =========================================================================
    with col_form:
        # Language Switcher Header
        lang_col1, lang_col2 = st.columns([1, 2])
        with lang_col1:
            st.caption("🌐 Language / भाषा")
        with lang_col2:
            lang_opts = ["mr", "hi", "en"]
            lang_choice = st.selectbox(
                "Language Selector",
                options=lang_opts,
                format_func=lambda x: "🚩 मराठी (Marathi)" if x == "mr" else ("🇮🇳 हिंदी (Hindi)" if x == "hi" else "🌐 English"),
                index=lang_opts.index(lang) if lang in lang_opts else 0,
                key="auth_lang_select_refined",
                label_visibility="collapsed",
            )
            if lang_choice != lang:
                set_language(lang_choice)
                st.rerun()

        # Tabs: Login, Register, Admin
        tab_login, tab_register, tab_admin = st.tabs([
            f"🔑 {t('login', lang)}",
            f"📝 {t('register', lang)}",
            "🛠️ ॲडमिन (Admin Portal)",
        ])

        # ---------------------------------------------------------------------
        # TAB 1: FARMER LOGIN
        # ---------------------------------------------------------------------
        with tab_login:
            st.markdown(
                textwrap.dedent("""
                <div style="margin: 8px 0 16px 0;">
                    <h3 style="margin: 0; color: #0b2316; font-size: 1.35rem; font-weight: 800;">
                        शेतकरी खात्यात प्रवेश करा
                    </h3>
                    <p style="margin: 4px 0 0 0; color: #4b5563; font-size: 0.95rem;">
                        Sign in to manage your crops, diary, expenses & market prices.
                    </p>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

            # Instant 1-Click Demo Farmer Access Buttons
            st.markdown(
                textwrap.dedent("""
                <div style="background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 16px; padding: 12px 14px; margin-bottom: 16px;">
                    <div style="font-size: 0.82rem; font-weight: 800; color: #166534; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px;">
                        ⚡ 1-Click Demo Reviewer Access
                    </div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

            demo_col1, demo_col2 = st.columns(2)
            with demo_col1:
                if st.button("🚀 रमेश पाटील (Ramesh Patil)", key="auth_demo_ramesh", use_container_width=True, type="primary"):
                    _perform_direct_login("9876543210", "Farmer@123", lang)
            with demo_col2:
                if st.button("🚀 विशाल सोनवणे (Vishal)", key="auth_demo_vishal", use_container_width=True):
                    _perform_direct_login("9637137197", "Farmer@123", lang)

            st.markdown(
                textwrap.dedent("""
                <div style="display: flex; align-items: center; text-align: center; color: #9ca3af; margin: 16px 0;">
                    <div style="flex-grow: 1; height: 1px; background: #e5e7eb;"></div>
                    <span style="padding: 0 12px; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: #6b7280;">or sign in manually</span>
                    <div style="flex-grow: 1; height: 1px; background: #e5e7eb;"></div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

            with st.form("manual_farmer_login_form", clear_on_submit=False):
                identifier = st.text_input(
                    f"📱 {t('phone', lang)} / ✉️ {t('email', lang)}",
                    placeholder="e.g. 9876543210 or ramesh.patil@example.com",
                    key="login_input_id",
                )
                password = st.text_input(
                    f"🔒 {t('password', lang)}",
                    type="password",
                    placeholder="Enter password (e.g. Farmer@123)",
                    key="login_input_pw",
                )
                login_btn = st.form_submit_button(f"🚀 {t('login', lang)}", use_container_width=True, type="primary")

                if login_btn:
                    if not identifier or not password:
                        st.error("Please enter your registered mobile number and password.")
                    else:
                        _perform_direct_login(identifier.strip(), password.strip(), lang)

        # ---------------------------------------------------------------------
        # TAB 2: FARMER REGISTRATION
        # ---------------------------------------------------------------------
        with tab_register:
            st.markdown(
                textwrap.dedent("""
                <div style="margin: 8px 0 16px 0;">
                    <h3 style="margin: 0; color: #0b2316; font-size: 1.35rem; font-weight: 800;">
                        नवीन शेतकरी नोंदणी करा
                    </h3>
                    <p style="margin: 4px 0 0 0; color: #4b5563; font-size: 0.95rem;">
                        Create your free farm management account in under 1 minute.
                    </p>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

            with st.form("refined_register_form", clear_on_submit=False):
                full_name = st.text_input(f"👤 {t('full_name', lang)} *", placeholder="e.g. Balasaheb Shinde")
                rc1, rc2 = st.columns(2)
                with rc1:
                    reg_phone = st.text_input(f"📱 {t('phone', lang)} *", placeholder="10-digit mobile number")
                with rc2:
                    reg_email = st.text_input(f"✉️ {t('email', lang)} (Optional)", placeholder="farmer@example.com")

                rp1, rp2 = st.columns(2)
                with rp1:
                    new_password = st.text_input(f"🔒 {t('password', lang)} *", type="password", placeholder="At least 6 characters")
                with rp2:
                    confirm_password = st.text_input(f"🔒 {t('confirm_password', lang)} *", type="password", placeholder="Repeat password")

                st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #166534; margin: 10px 0 6px 0;'>🌾 शेती व जमिनीचा तपशील (Farm Location)</div>", unsafe_allow_html=True)
                rloc1, rloc2, rloc3 = st.columns(3)
                with rloc1:
                    reg_state = st.selectbox(
                        f"📍 {t('state', lang)}",
                        options=["Maharashtra", "Punjab", "Madhya Pradesh", "Gujarat", "Karnataka", "Uttar Pradesh", "Telangana", "Andhra Pradesh", "Rajasthan", "Haryana", "Bihar", "West Bengal", "Tamil Nadu"],
                        index=0,
                    )
                with rloc2:
                    reg_district = st.text_input(f"🏙️ {t('district', lang)}", placeholder="e.g. Pune, Nashik")
                with rloc3:
                    reg_village = st.text_input(f"🏡 {t('village', lang)}", placeholder="e.g. Baramati")

                rf1, rf2, rf3 = st.columns(3)
                with rf1:
                    reg_farm_size = st.number_input(f"📐 {t('farm_size', lang)} (Acres)", min_value=0.0, max_value=500.0, value=2.0, step=0.5)
                with rf2:
                    reg_soil = st.selectbox(
                        f"🌱 {t('soil_type', lang)}",
                        options=["Black Clay (काळी माती)", "Red Loam (तांबडी माती)", "Alluvial (गाळाची माती)", "Sandy Loam (वाळूमिश्रित)", "Medium Black (मध्यम काळी)"],
                        index=0,
                    )
                with rf3:
                    reg_irrig = st.selectbox(
                        f"💧 {t('irrigation', lang)}",
                        options=["Drip Irrigation (ठिबक)", "Sprinkler (तुषार)", "Flood / Canal (पाटपाणी)", "Borewell / Well", "Rainfed (कोरडवाहू)"],
                        index=0,
                    )

                # DPDP Act 2023 Consent Card
                dpdp_consent = st.checkbox(
                    "मी डिजिटल वैयक्तिक डेटा संरक्षण कायदा (DPDP Act, 2023) अंतर्गत माझ्या शेती डेटाच्या सुरक्षित साठवणुकीस संमती देतो. / "
                    "I consent to the processing and secure storage of my agricultural data under DPDP Act 2023.",
                    value=True,
                )

                reg_submitted = st.form_submit_button(f"✅ {t('register', lang)}", use_container_width=True, type="primary")

                if reg_submitted:
                    if not dpdp_consent:
                        st.error("You must agree to the DPDP Act 2023 privacy notice to create an account.")
                    else:
                        try:
                            with get_db() as db:
                                reg_payload = UserRegister(
                                    full_name=full_name,
                                    phone=reg_phone or None,
                                    email=reg_email or None,
                                    password=new_password,
                                    confirm_password=confirm_password,
                                    preferred_language=lang,
                                    state=reg_state,
                                    district=reg_district or None,
                                    village=reg_village or None,
                                    farm_size=reg_farm_size,
                                    farm_area_unit="Acre",
                                    soil_type=reg_soil,
                                    irrigation_method=reg_irrig,
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
                                    must_change_password=getattr(new_user, "must_change_password", False),
                                )
                                set_current_farmer(auth_farmer)
                                st.success(f"Welcome to AgriSaathi AI, {new_user.full_name}!")
                                st.rerun()
                        except (ValidationError, DuplicateRecordError) as e:
                            st.error(f"⚠️ {str(e)}")
                        except Exception as e:
                            st.error(f"Registration error: {str(e)}")

        # ---------------------------------------------------------------------
        # TAB 3: ADMINISTRATOR PORTAL
        # ---------------------------------------------------------------------
        with tab_admin:
            st.markdown(
                textwrap.dedent("""
                <div style="margin: 8px 0 16px 0;">
                    <h3 style="margin: 0; color: #0b2316; font-size: 1.35rem; font-weight: 800;">
                        🛠️ Developer & Enterprise Admin Portal
                    </h3>
                    <p style="margin: 4px 0 0 0; color: #4b5563; font-size: 0.95rem;">
                        Restricted administrative telemetry, farmer controls & data management.
                    </p>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

            primary_admin_email = (settings.ADMIN_EMAIL or "sonwanevishal1361@gmail.com").strip().lower()
            primary_admin_pw = (settings.ADMIN_PASSWORD or "vishal1361").strip()

            # 1-Click Quick Admin Access
            if st.button(f"🚀 Administrator Quick Access ({primary_admin_email})", key="auth_demo_admin_btn", use_container_width=True, type="primary"):
                try:
                    with get_db() as db:
                        UserService.seed_admin_if_missing(db)
                        admin_user = UserService.authenticate_farmer(
                            db,
                            UserLogin(identifier=primary_admin_email, password=primary_admin_pw),
                        )
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
                            must_change_password=getattr(admin_user, "must_change_password", False),
                        )
                        set_current_farmer(auth_admin)
                        set_page("admin")
                        st.rerun()
                except Exception as e:
                    st.error(f"Admin login error: {str(e)}")

            st.markdown(
                textwrap.dedent("""
                <div style="display: flex; align-items: center; text-align: center; color: #9ca3af; margin: 14px 0;">
                    <div style="flex-grow: 1; height: 1px; background: #e5e7eb;"></div>
                    <span style="padding: 0 12px; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: #6b7280;">or enter credentials</span>
                    <div style="flex-grow: 1; height: 1px; background: #e5e7eb;"></div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

            with st.form("refined_admin_form", clear_on_submit=False):
                admin_id = st.text_input("👤 Admin Email / Phone", value=primary_admin_email, placeholder="e.g. sonwanevishal1361@gmail.com", key="admin_auth_user")
                admin_pw = st.text_input("🔒 Administrator Password", type="password", placeholder="Enter administrator password", key="admin_auth_pw")
                admin_sub = st.form_submit_button("🚀 Authenticate Admin Access", use_container_width=True)

                if admin_sub:
                    if not admin_id or not admin_pw:
                        st.error("Please enter both administrator identifier and password.")
                    else:
                        try:
                            with get_db() as db:
                                UserService.seed_admin_if_missing(db)
                                admin_user = UserService.authenticate_farmer(
                                    db,
                                    UserLogin(identifier=admin_id.strip(), password=admin_pw.strip()),
                                )
                                if getattr(admin_user, "role", "farmer") != "admin":
                                    raise AuthenticationError("Access denied: Account lacks administrator privileges.")

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
                                    must_change_password=getattr(admin_user, "must_change_password", False),
                                )
                                set_current_farmer(auth_admin)
                                set_page("admin")
                                AdminService.log_action(
                                    db=db,
                                    admin=auth_admin,
                                    action="LOGIN",
                                    resource_type="system",
                                    details={"portal": "split_screen_auth"},
                                )
                                st.rerun()
                        except AuthenticationError as e:
                            st.error(f"❌ {e.message}")
                        except Exception as e:
                            st.error(f"Admin authentication error: {str(e)}")


def render_force_password_change(farmer: AuthenticatedFarmer):
    """Force farmer/administrator to change their initial password before accessing the system."""
    st.markdown(
        textwrap.dedent("""
        <div style="background: #fff3e0; border: 2px solid #ffb74d; border-radius: 16px; padding: 20px; margin-bottom: 25px;">
            <h3 style="margin: 0; color: #e65100; font-weight: 800;">
                🔒 आवश्यक सुरक्षा बदल: पासवर्ड बदला (Mandatory Password Change)
            </h3>
            <p style="margin: 6px 0 0 0; color: #424242; font-size: 1rem;">
                सुरक्षेच्या कारणास्तव, प्रथमच लॉगिन करताना नवीन पासवर्ड तयार करणे बंधनकारक आहे.
            </p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    with st.form("force_password_change_form"):
        old_password = st.text_input("सध्याचा / तात्पुरता पासवर्ड (Current Password) *", type="password")
        new_password = st.text_input("नवीन पासवर्ड (New Password) *", type="password", help="किमान 8 अक्षरे, एक मोठा अक्षर, एक लहान अक्षर, एक अंक व एक विशेष चिन्ह (@$!%*?&)")
        confirm_password = st.text_input("नवीन पासवर्ड पुन्हा टाका (Confirm Password) *", type="password")

        submitted = st.form_submit_button("✅ पासवर्ड बदला व पुढे जा (Change Password & Proceed)", use_container_width=True, type="primary")

        if submitted:
            if not old_password or not new_password or not confirm_password:
                st.error("सर्व फील्ड भरणे आवश्यक आहे.")
            elif new_password != confirm_password:
                st.error("नवीन पासवर्ड जुळत नाही.")
            else:
                try:
                    with get_db() as db:
                        UserService.change_password(
                            db=db,
                            farmer_id=farmer.id,
                            old_password=old_password,
                            new_password=new_password,
                            confirm_password=confirm_password,
                        )
                        st.success("पासवर्ड यशस्वीरीत्या बदलला गेला!")
                        farmer.must_change_password = False
                        set_current_farmer(farmer)
                        st.rerun()
                except (ValidationError, AuthenticationError) as e:
                    st.error(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error(f"त्रुटी: {str(e)}")
