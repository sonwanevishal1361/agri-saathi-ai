"""Government Agricultural Schemes UI page."""

import streamlit as st
from services.schemes_service import SchemesService
from core.auth import AuthenticatedFarmer
from ui.state import get_language


def render_schemes_page(farmer: AuthenticatedFarmer):
    """Render verified government agricultural schemes and subsidy guidance."""
    lang = get_language()

    st.title("🏛️ शासकीय कृषी योजना व अनुदान (Government Schemes)")
    st.markdown(
        "शेतकऱ्यांसाठी केंद्र व राज्य शासनाच्या अधिकृत कल्याणकारी योजना, पात्रता निकष व अर्ज प्रक्रिया."
    )

    f1, f2, f3 = st.columns([3, 2, 2])
    with f1:
        search = st.text_input("🔍 योजना शोधा (Search Scheme)", placeholder="उदा. PM-Kisan, पीक विमा, ठिबक अनुदान...")
    with f2:
        cat = st.selectbox(
            "📂 वर्गवारी (Category)",
            options=["All", "Income Support", "Crop Insurance", "Soil & Nutrients", "Micro-Irrigation & Water", "Credit & Loans", "Market & Trading"],
        )
    with f3:
        scope = st.selectbox("🌐 व्याप्ती (Scope)", options=["All", "National", "Maharashtra"])

    schemes = SchemesService.filter_schemes(search=search or None, category=cat, scope=scope)

    st.markdown(f"##### 📜 उपलब्ध योजनांची यादी ({len(schemes)})")

    if not schemes:
        st.info("कोणतीही योजना आढळली नाही.")
    else:
        for s in schemes:
            with st.container(border=True):
                s_name = s.get("marathi_name") if lang == "mr" else (s.get("hindi_name") if lang == "hi" else s.get("name"))
                st.markdown(f"### 🏛️ {s_name}")
                st.caption(f"अधिकृत इंग्रजी नाव: {s.get('name')} | वर्ग: `{s.get('category')}` | व्याप्ती: `{s.get('scope')}`")
                st.markdown(f"**वर्णन:** {s.get('description')}")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("##### 🎁 योजनेचे लाभ (Benefits)")
                    st.info(s.get("benefits_summary"))
                with col2:
                    st.markdown("##### 📋 पात्रता निकष (Eligibility)")
                    st.warning(s.get("eligibility_summary"))

                st.markdown("##### 📝 अर्ज कसा करावा? (Application Process)")
                st.markdown(s.get("application_process"))

                st.markdown("---")
                link_col, stat_col = st.columns([3, 2])
                with link_col:
                    st.markdown(f"🔗 **अधिकृत पोर्टल:** [{s.get('official_url')}]({s.get('official_url')})")
                with stat_col:
                    st.caption(f"सत्यापित तारीख: {s.get('last_verified')} | `{s.get('verification_status')}`")

    st.markdown("---")
    st.caption(
        "महत्त्वाची सूचना: AgriSaathi AI हे थेट अर्ज स्वीकारत नाही. अर्ज करण्यासाठी कृपया शासनाच्या दिलेल्या अधिकृत पोर्टलवर किंवा जवळच्या आपले सरकार सेवा केंद्र / CSC वर संपर्क साधावा."
    )
