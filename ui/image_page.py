"""Crop Image Upload and Symptom Assessment UI page."""

import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.image_service import ImageService
from config import settings
from utils.formatting import format_date


def render_image_page(farmer: AuthenticatedFarmer):
    """Render crop image upload, symptom analysis questionnaire, and health diary."""
    st.title("🔬 पीक आरोग्य तपासणी व लक्षण निदान (Crop Health & Symptom Analyzer)")
    st.markdown(
        "पिकावरील रोगाची किंवा किडीची लक्षणे निवडून ICAR मार्गदर्शक तत्त्वांनुसार प्रमाणित प्राथमिक सल्ला मिळवा."
    )

    # Honesty and transparency note regarding AI model
    st.info(
        "ℹ️ **पारदर्शकता सूचना (Model Notice)**: सध्या संगणकावरील स्थानिक AI मॉडेल (Qwen 2.5 3B) हे केवळ मजकूर व कृषी तार्किक विश्लेषणासाठी कार्यरत आहे. "
        "चुकीचे रासायनिक प्रमाण टाळण्यासाठी थेट फोटोवरून स्वयंचलित रोग निदान बंद ठेवले आहे. आपण फोटो सुरक्षित रेकॉर्डसाठी अपलोड करू शकता व खालील लक्षण प्रश्नावलीद्वारे शास्त्रोक्त सल्ला मिळवू शकता."
    )

    with get_db() as db:
        farmer_crops = CropService.list_crops(db, farmer.id)
        past_observations = ImageService.list_farmer_observations(db, farmer.id)

    tab_check, tab_history = st.tabs([
        "🌿 नवीन तपासणी (New Symptom Check)",
        f"📋 जुन्या आरोग्य नोंदी (Health Diary) [{len(past_observations)}]",
    ])

    with tab_check:
        with st.form("form_symptom_check", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                crop_dict = {"None": "इतर / नवीन पीक"}
                for cr in farmer_crops:
                    crop_dict[cr.id] = f"{cr.name} ({cr.variety or 'General'})"
                crop_sel = st.selectbox(
                    "🌾 बाधित पीक निवडा (Select Crop) *",
                    options=list(crop_dict.keys()),
                    format_func=lambda k: crop_dict[k],
                )
                plant_part = st.selectbox(
                    "🍃 बाधित भाग (Affected Plant Part) *",
                    options=["Leaves (पाने)", "Stem / Shoot (खोड / फांद्या)", "Boll / Pod / Fruit (बोंड / शेंग / फळ)", "Roots (मुळे / बुंधा)", "Whole Plant (संपूर्ण रोप)"],
                )
                onset = st.selectbox(
                    "⏱️ लक्षणे दिसण्याचा कालावधी (Onset)",
                    options=["Gradual - 1-2 weeks (हळूहळू पसरत आहे)", "Sudden - 2-3 days (अचानक २-३ दिवसांत)", "After Rain (पावसानंतर लगेच)"],
                )

            with c2:
                uploaded_file = st.file_uploader(
                    "📷 पिकाचा फोटो अपलोड करा (Optional Photo Upload)",
                    type=["jpg", "jpeg", "png"],
                    help=f"जास्तीत जास्त आकार: {settings.MAX_UPLOAD_SIZE_MB} MB",
                )
                symptom_text = st.text_area(
                    "📝 दिसणारी लक्षणे व समस्या सांगा (Describe Observed Symptoms) *",
                    placeholder="उदा. पानाच्या मागील बाजूस पांढरी माशी दिसत आहे, पाने पिवळी पडत असून वरच्या बाजूला गोळा होत आहेत...",
                )

            submitted = st.form_submit_button("🔍 लक्षणांचे विश्लेषण करा (Analyze Symptoms)", use_container_width=True)

            if submitted:
                if not symptom_text.strip():
                    st.error("कृपया दिसणाऱ्या लक्षणांचे थोडक्यात वर्णन करा.")
                else:
                    saved_img_name = None
                    if uploaded_file is not None:
                        try:
                            file_bytes = uploaded_file.read()
                            saved_img_name = ImageService.save_uploaded_crop_image(file_bytes, uploaded_file.name)
                            st.success("📷 फोटो यशस्वीरीत्या सुरक्षित साठवला गेला.")
                        except Exception as e:
                            st.warning(f"फोटो अपलोड त्रुटी: {str(e)}")

                    crop_name_for_analysis = "General"
                    if crop_sel != "None":
                        matching_c = next((c for c in farmer_crops if c.id == crop_sel), None)
                        if matching_c:
                            crop_name_for_analysis = matching_c.name

                    analysis = ImageService.analyze_crop_symptoms(
                        crop_name=crop_name_for_analysis,
                        symptom_text=symptom_text,
                        plant_part=plant_part.split(" (")[0],
                        onset=onset.split(" -")[0],
                    )

                    with get_db() as db:
                        crop_id_val = crop_sel if crop_sel != "None" else None
                        ImageService.record_health_observation(
                            db=db,
                            farmer_id=farmer.id,
                            crop_id=crop_id_val,
                            symptom_description=symptom_text,
                            image_storage_path=saved_img_name,
                            analysis_result=analysis,
                        )

                    st.markdown("---")
                    st.markdown("### 📊 प्राथमिक विश्लेषण निकाल (Assessment Result)")

                    if analysis.get("diagnoses"):
                        for diag in analysis["diagnoses"]:
                            with st.container(border=True):
                                st.markdown(f"#### ⚠️ संभाव्य समस्या: {diag.get('condition')}")
                                st.markdown(f"**प्राथमिक कारणे:** {diag.get('causes')}")
                                st.markdown("##### 🛡️ विद्यापीठ शिफारशीनुसार उपाययोजना:")
                                st.markdown(diag.get("management"))
                                st.caption(f"स्रोत: {diag.get('source')}")
                    else:
                        st.info("विशिष्ट रोग जुळला नाही. सर्वसाधारण सल्ला:")
                        st.write(analysis.get("general_advice"))

                    st.warning(f"🛡️ **सुरक्षा सूचना:** {analysis.get('safety_disclaimer')}")

    # ---------------- TAB 2: HEALTH DIARY ----------------
    with tab_history:
        if not past_observations:
            st.info("कोणत्याही मागील तपासणी नोंदी नाहीत.")
        else:
            for obs in past_observations:
                with st.container(border=True):
                    crop_title = f"🌾 {obs.crop.name} | " if obs.crop else ""
                    st.markdown(f"**{crop_title}तपासणी दिनांक: {format_date(obs.created_at)}**")
                    st.markdown(f"**लक्षणे:** {obs.symptom_description}")
                    if obs.possible_causes:
                        st.caption(f"{obs.possible_causes}")
                    if obs.advice_summary:
                        st.info(f"**दिलेला सल्ला:**\n{obs.advice_summary}")
                    st.caption(f"संदर्भ: {obs.source_reference or 'ICAR Guidelines'}")
