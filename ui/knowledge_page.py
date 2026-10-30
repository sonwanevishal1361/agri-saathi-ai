"""Crop Knowledge Library and Agronomic Reference UI page."""

import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.knowledge_service import KnowledgeService
from models.knowledge import KnowledgeDocument


def render_knowledge_page(farmer: AuthenticatedFarmer):
    """Render verified agricultural knowledge library and RAG document explorer."""
    st.title("📚 कृषी ज्ञान ग्रंथालय (Crop Knowledge Library)")
    st.markdown(
        "भारतीय कृषी संशोधन परिषद (ICAR), मध्यवर्ती संशोधन संस्था व राज्य कृषी विद्यापीठांच्या "
        "अधिकृत संशोधन निष्कर्षांवर आधारित प्रमाणित शेती मार्गदर्शक."
    )

    tab_crops, tab_docs = st.tabs([
        "🌾 पिकांची अधिकृत माहिती (Crop Guidelines)",
        "📄 सत्यापित कृषी दस्तऐवज (Verified RAG Documents)",
    ])

    # ---------------- TAB 1: CROPS KNOWLEDGE ----------------
    with tab_crops:
        search_query = st.text_input("🔍 पीक किंवा रोगाचे नाव शोधा (Search Crop or Topic)", placeholder="उदा. Cotton, Soybean, बोंडअळी, खत नियोजन...")

        with get_db() as db:
            crops_knowledge = KnowledgeService.list_all_crops_knowledge(db, search=search_query or None)

        if not crops_knowledge:
            st.info("या शोधासाठी कोणतीही पिके आढळली नाहीत.")
        else:
            for ck in crops_knowledge:
                with st.expander(f"🌾 **{ck.crop_name}** ({ck.scientific_name or ''}) - [सत्यापित माहिती]", expanded=False):
                    st.markdown(f"**वर्णन:** {ck.description}")
                    st.markdown("---")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("##### 🌍 माती व हवामान (Soil & Climate)")
                        st.markdown(f"**मातीची गरज:** {ck.soil_requirements}")
                        st.markdown(f"**हवामान:** {ck.climate_requirements}")

                        st.markdown("##### 🌱 पेरणी व लागवड (Sowing)")
                        st.markdown(ck.sowing_information)

                        st.markdown("##### 💧 पाणी व्यवस्थापन (Irrigation)")
                        st.markdown(ck.irrigation_information)

                    with col2:
                        st.markdown("##### 🧪 खत व्यवस्थापन (Nutrient Management)")
                        st.markdown(ck.nutrient_management)

                        st.markdown("##### 🐛 कीड व रोग नियंत्रण (Pest & Disease IPM)")
                        st.markdown(ck.pest_disease_information)

                        st.markdown("##### ✂️ काढणी व साठवण (Harvesting & Post-Harvest)")
                        st.markdown(ck.harvesting_information)

                    st.markdown("---")
                    st.caption(f"स्रोत: **{ck.source_name}** | [अधिकृत संशोधन पोर्टल]({ck.source_url}) | स्थिती: `{ck.verification_status}`")

    # ---------------- TAB 2: RAG DOCUMENTS ----------------
    with tab_docs:
        st.markdown("##### 📑 कृषी सहाय्यकाचे ज्ञान दस्तऐवज (RAG Knowledge Passages)")
        st.caption("AI सहाय्यक प्रश्नांची उत्तरे देताना या दस्तऐवजांचा संदर्भ घेतो, ज्यामुळे काल्पनिक माहिती टाळली जाते.")

        with get_db() as db:
            docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()

        for d in docs:
            with st.container(border=True):
                st.markdown(f"#### 📄 {d.title}")
                st.markdown(f"**विषय (Topic):** `{d.topic}` | **भाषा:** `{d.language}` | **स्थिती:** `{d.verification_status}`")
                st.markdown(f"> {d.content}")
                st.caption(f"अधिकृत संदर्भ: [{d.source_name}]({d.source_url})")
