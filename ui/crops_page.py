"""Crop Management UI page."""

from datetime import date, timedelta
import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from schemas.crop import CropCreate
from services.crop_service import CropService
from utils.formatting import format_date
from utils.language import t
from ui.state import get_language, set_page
from core.exceptions import ValidationError


COMMON_INDIAN_CROPS = [
    "Cotton (कापूस)",
    "Soybean (सोयाबीन)",
    "Wheat (गहू)",
    "Rice / Paddy (भात / धान)",
    "Tomato (टोमॅटो)",
    "Onion (कांदा)",
    "Sugarcane (ऊस)",
    "Maize / Corn (मका)",
    "Gram / Chana (हरभरा / चना)",
    "Tur / Arhar (तूर)",
    "Groundnut (भुईमूग)",
    "Pomegranate (डाळिंब)",
    "Banana (केळी)",
    "Ginger (आले)",
    "Turmeric (हळद)",
    "Other (इतर)",
]

GROWTH_STAGES = [
    "Sowing / Nursery (पेरणी / रोपवाटिका)",
    "Germination / Emergence (उगवण)",
    "Vegetative Growth (शाकीय वाढ)",
    "Tillering / Branching (फुटवे / फांद्या फुटणे)",
    "Squaring / Budding (कळ्या भरणे)",
    "Flowering (फुलोरा)",
    "Fruit / Boll / Pod Formation (फळे / बोंड / शेंगा लागणे)",
    "Grain / Fruit Filling (दाणे भरणे)",
    "Maturity / Ripening (पक्वता)",
    "Ready for Harvest (कापणीस तयार)",
]


def render_crops_page(farmer: AuthenticatedFarmer):
    """Render crop listing and creation page."""
    lang = get_language()

    st.title(f"🌾 {t('my_crops', lang)}")

    with get_db() as db:
        active_crops = CropService.list_crops(db, farmer.id, status="active")
        harvested_crops = CropService.list_crops(db, farmer.id, status="harvested")

    # Add Crop Form Expander
    with st.expander(f"➕ {t('btn_register_new_crop', lang)}", expanded=len(active_crops) == 0):
        with st.form("add_crop_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                crop_select = st.selectbox("🌾 पीक निवडा (Select Crop) *", options=COMMON_INDIAN_CROPS)
                custom_name = None
                if "Other" in crop_select:
                    custom_name = st.text_input("पिकाचे नाव प्रविष्ट करा (Enter Crop Name) *")
                crop_final_name = custom_name.strip() if custom_name else crop_select.split(" (")[0].strip()

                variety = st.text_input("वाण / जात (Variety / Hybrid)", placeholder="e.g. Ajit-155, JS-335, Lokwan")
                plot_name = st.text_input("तुकडा / शेताचे नाव (Plot / Field Name)", placeholder="e.g. विहिरीचे रान, गट नं. ४२")

            with c2:
                area = st.number_input("लागवड क्षेत्र (Area in Acres) *", min_value=0.1, max_value=500.0, value=2.0, step=0.5)
                sowing_date = st.date_input("पेरणीची तारीख (Sowing Date) *", value=date.today())
                default_harvest = sowing_date + timedelta(days=120)
                expected_harvest = st.date_input("अपेक्षित काढणी तारीख (Expected Harvest Date)", value=default_harvest)

            c3, c4 = st.columns(2)
            with c3:
                soil = st.selectbox(
                    "मातीचा प्रकार (Soil Type)",
                    options=["Black Clay (काळी कसदार)", "Medium Black (मध्यम काळी)", "Red Loam (तांबडी)", "Sandy Loam (वाळूमिश्रित)", "Light / Shallow (हलकी जमीन)"],
                )
                stage = st.selectbox("सध्याची अवस्था (Growth Stage)", options=GROWTH_STAGES)
            with c4:
                irrigation = st.selectbox(
                    "पाणी व्यवस्थापन (Irrigation Method)",
                    options=["Drip (ठिबक सिंचन)", "Sprinkler (तुषार सिंचन)", "Flood (पाटपाणी / प्रवाह)", "Rainfed (कोरडवाहू / केवळ पावसावर)"],
                )
                notes = st.text_area("नोंद / विशेष शेरा (Notes)", placeholder="बियाणे दर, कंपनी किंवा खतांची माहिती")

            submitted = st.form_submit_button(f"✅ {t('btn_save_crop', lang)}", use_container_width=True)

            if submitted:
                if not crop_final_name:
                    st.error("कृपया पिकाचे नाव प्रविष्ट करा." if lang == "mr" else ("कृपया फसल का नाम दर्ज करें।" if lang == "hi" else "Please enter crop name."))
                else:
                    try:
                        with get_db() as db:
                            new_crop = CropService.create_crop(
                                db=db,
                                farmer_id=farmer.id,
                                crop_in=CropCreate(
                                    name=crop_final_name,
                                    variety=variety or None,
                                    plot_name=plot_name or None,
                                    area=area,
                                    area_unit="Acre",
                                    sowing_date=sowing_date,
                                    expected_harvest_date=expected_harvest,
                                    soil_type=soil,
                                    irrigation_method=irrigation,
                                    growth_stage=stage.split(" (")[0],
                                    status="active",
                                    notes=notes or None,
                                ),
                            )
                            st.success(f"पीक यशस्वीरीत्या नोंदवले: {new_crop.name} ({new_crop.area} एकर)" if lang == "mr" else f"Crop registered successfully: {new_crop.name}")
                            st.rerun()
                    except ValidationError as e:
                        st.error(f"⚠️ {str(e)}")
                    except Exception as e:
                        st.error(f"त्रुटी: {str(e)}" if lang == "mr" else f"Error: {str(e)}")

    st.markdown("---")

    tab_active, tab_harvested = st.tabs([
        f"🟢 {t('active_crops_tab', lang)} [{len(active_crops)}]",
        f"🌾 {t('harvested_crops_tab', lang)} [{len(harvested_crops)}]",
    ])

    with tab_active:
        if not active_crops:
            st.markdown(
                f"""
                <div class="empty-state-box">
                    <div class="empty-state-icon">🌾</div>
                    <h4 style="margin: 0; color: #1b5e20;">{t('empty_crops_title', lang)}</h4>
                    <p style="color: #4b634b; font-size: 0.95rem; margin: 8px 0 0 0;">{t('empty_crops_desc', lang)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for crop in active_crops:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.markdown(f"### 🌾 {crop.name}")
                        st.markdown(f"**वाण:** {crop.variety or 'साधारण'} | **शेत:** {crop.plot_name or 'मुख्य शेत'}")
                        st.caption(f"पेरणी: {format_date(crop.sowing_date)} | अंदाजे काढणी: {format_date(crop.expected_harvest_date)}")
                    with col2:
                        st.metric(label="लागवड क्षेत्र", value=f"{crop.area} {crop.area_unit}")
                        st.markdown(f"**अवस्था:** `{crop.growth_stage}`")
                        st.markdown(f"**सिंचन:** {crop.irrigation_method or 'N/A'}")
                    with col3:
                        st.write("")
                        if st.button(f"🔍 {t('view_details', lang)}", key=f"btn_view_{crop.id}", use_container_width=True):
                            set_page("crop_detail", crop_id=crop.id)
                            st.rerun()
                        if st.button(f"🤖 {t('nav_ask_ai', lang)}", key=f"btn_ask_ai_{crop.id}", use_container_width=True):
                            st.session_state["chat_crop_filter"] = crop.id
                            set_page("chat")
                            st.rerun()

    with tab_harvested:
        if not harvested_crops:
            st.info("कोणतीही काढणी झालेली पिके नोंदवलेली नाहीत." if lang == "mr" else ("कोई काटी गई फसल दर्ज नहीं है।" if lang == "hi" else "No harvested crops recorded."))
        else:
            for crop in harvested_crops:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.markdown(f"### 🌾 {crop.name} (काढणी पूर्ण)")
                        st.caption(f"पेरणी: {format_date(crop.sowing_date)} | काढणी तारीख: {format_date(crop.actual_harvest_date or crop.expected_harvest_date)}")
                    with col2:
                        st.metric(label="एकूण क्षेत्र", value=f"{crop.area} {crop.area_unit}")
                    with col3:
                        if st.button(f"🔍 {t('view_details', lang)}", key=f"btn_harvested_{crop.id}", use_container_width=True):
                            set_page("crop_detail", crop_id=crop.id)
                            st.rerun()
