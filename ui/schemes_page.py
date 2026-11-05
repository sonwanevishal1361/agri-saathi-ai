"""Government Agricultural Schemes UI page for Indian Farmers.

Featuring benefit pills, eligibility highlights, large touch links,
and browser Web Speech voice support.
"""

import textwrap
import streamlit as st
from services.schemes_service import SchemesService
from core.auth import AuthenticatedFarmer
from ui.state import get_language
from ui.components.voice_button import render_voice_mic_button, render_speaker_button


def render_schemes_page(farmer: AuthenticatedFarmer):
    """Render verified government agricultural schemes and subsidy guidance."""
    lang = get_language()

    st.markdown(
        textwrap.dedent("""
        <div class="agri-hero-banner" style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="display: inline-block; background: rgba(255,255,255,0.18); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; margin-bottom: 8px;">
                        🏛️ शासकीय योजना • थेट सबसिडी व अनुदान
                    </div>
                    <h2 style="margin: 0; color: #ffffff; font-size: 1.8rem; font-weight: 800;">
                        शासकीय कृषी योजना व अनुदान
                    </h2>
                    <div style="color: rgba(255,255,255,0.88); font-size: 0.95rem; margin-top: 4px;">
                        केंद्र व राज्य शासनाच्या अधिकृत कल्याणकारी योजना, पात्रता निकष व थेट अर्ज लिंक्स
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="background: rgba(255,255,255,0.2); backdrop-filter: blur(8px); padding: 6px 14px; border-radius: 12px; color: #ffffff; font-weight: 700; font-size: 0.9rem;">
                        🇮🇳 Verified Gov Portals
                    </span>
                </div>
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    # Voice Assistant Controls
    v_c1, v_c2 = st.columns([1, 1])
    with v_c1:
        render_voice_mic_button(lang, prompt_placeholder="🎙️ योजनेचे नाव सांगा (Speak scheme name)")
    with v_c2:
        render_speaker_button("केंद्र व राज्य शासनाच्या अनुदानाच्या योजनांची माहिती, आवश्यक कागदपत्रे व अर्ज प्रक्रिया येथे पहा.", lang)

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
        st.markdown(
            textwrap.dedent("""
            <div class="empty-state-box">
                <div class="empty-state-icon">🏛️</div>
                <h3 style="margin: 0; color: #1b5e20; font-weight: 800;">कोणतीही योजना आढळली नाही</h3>
                <p style="color: #4b634b; font-size: 1rem; margin: 8px 0 0 0;">
                    कृपया इतर शब्द किंवा वर्गवारी बदलून शोधा.
                </p>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )
    else:
        for s in schemes:
            with st.container(border=True):
                s_name = s.get("marathi_name") if lang == "mr" else (s.get("hindi_name") if lang == "hi" else s.get("name"))
                st.markdown(
                    textwrap.dedent(f"""
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                        <div>
                            <h3 style="margin: 0; color: #1b5e20; font-size: 1.4rem; font-weight: 800;">🏛️ {s_name}</h3>
                            <span style="font-size: 0.88rem; color: #4b634b; font-weight: 600;">{s.get('name')}</span>
                        </div>
                        <div style="display: flex; gap: 6px;">
                            <span style="background: #e8f5e9; color: #1b5e20; border: 1.5px solid #81c784; font-size: 0.82rem; font-weight: 700; padding: 4px 10px; border-radius: 12px;">
                                {s.get('category')}
                            </span>
                            <span style="background: #fff8e1; color: #6d4c41; border: 1.5px solid #ffe082; font-size: 0.82rem; font-weight: 700; padding: 4px 10px; border-radius: 12px;">
                                {s.get('scope')}
                            </span>
                        </div>
                    </div>
                    """).strip(),
                    unsafe_allow_html=True,
                )
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
                    st.link_button(
                        f"🔗 अधिकृत पोर्टलवर जा ({s.get('name')})",
                        url=s.get("official_url"),
                        use_container_width=True,
                    )
                with stat_col:
                    st.caption(f"सत्यापित तारीख: {s.get('last_verified')} | `{s.get('verification_status')}`")
