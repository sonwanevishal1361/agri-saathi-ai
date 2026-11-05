"""Farm Activity Diary UI page for Indian Farmers.

Featuring oversized touch targets, voice dictation for diary notes,
speech read-aloud, and high-contrast clear records.
"""

from datetime import date
import textwrap
import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.activity_service import ActivityService
from schemas.activity import ActivityCreate
from utils.formatting import format_inr, format_date
from utils.language import t
from ui.state import get_language
from core.exceptions import ValidationError
from ui.components.voice_button import render_voice_mic_button, render_speaker_button
from ui.components.card import render_metric_card
from ui.components.icons import get_svg_icon


ACTIVITY_TYPES = [
    "Sowing (पेरणी)",
    "Weeding / Hoeing (खुरपणी / कोळपणी)",
    "Fertilizer Application (खत देणे)",
    "Pesticide / Fungicide Spraying (औषध फवारणी)",
    "Irrigation (पाणी देणे)",
    "Interculturing / Ploughing (नांगरणी / मशागत)",
    "Pruning / Staking (छाटणी / आधार देणे)",
    "Harvesting / Picking (तोडणी / काढणी)",
    "Post-Harvest / Grading (प्रतवारी / साठवण)",
    "Other (इतर)",
]


def render_diary_page(farmer: AuthenticatedFarmer):
    """Render the farm activity diary page."""
    lang = get_language()

    with get_db() as db:
        farmer_crops = CropService.list_crops(db, farmer.id)
        all_activities = ActivityService.list_activities(db, farmer.id, limit=200)

    tot_cost = sum(a.cost or 0.0 for a in all_activities)

    # Hero Banner
    calendar_icon = get_svg_icon("calendar", size=18, color="#ffffff")
    st.markdown(
        textwrap.dedent(f"""
        <div class="agri-hero-banner" style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.18); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; margin-bottom: 8px;">
                        {calendar_icon} {t('farm_diary', lang)} • शेती दैनंदिनी
                    </div>
                    <h2 style="margin: 0; color: #ffffff; font-size: 1.8rem; font-weight: 800;">
                        {t('farm_diary', lang)}
                    </h2>
                    <div style="color: rgba(255,255,255,0.88); font-size: 0.95rem; margin-top: 4px;">
                        पेरणी, फवारणी, खत व्यवस्थापन आणि मजुरीच्या सर्व दैनंदिन नोंदी एकाच ठिकाणी
                    </div>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <div style="background: rgba(255,255,255,0.2); backdrop-filter: blur(8px); padding: 8px 14px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.85); font-weight: 600;">एकूण नोंदी</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff;">{len(all_activities)}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); backdrop-filter: blur(8px); padding: 8px 14px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.85); font-weight: 600;">एकूण कृती खर्च</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #ffe082;">{format_inr(tot_cost)}</div>
                    </div>
                </div>
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    # Voice Assistant Controls
    v_c1, v_c2 = st.columns([1, 1])
    with v_c1:
        render_voice_mic_button(lang, prompt_placeholder="🎙️ शेती काम बोला (Speak activity note)")
    with v_c2:
        render_speaker_button("तुमच्या शेतातील दैनंदिन कामे जसे की पेरणी, खुरपणी, खते व फवारणीची नोंद येथे ठेवा.", lang)

    # Top metrics via reusable cards
    m1, m2 = st.columns(2)
    with m1:
        render_metric_card(
            label="एकूण नोंदी (Total Activities)",
            value=f"{len(all_activities)}",
            icon="📅",
        )
    with m2:
        render_metric_card(
            label="कृतींशी संबंधित खर्च (Activity Costs)",
            value=format_inr(tot_cost),
            icon="💸",
        )

    st.markdown("---")

    # Add Activity Expander
    with st.expander("➕ नवीन शेती कृती नोंदवा (Add Farm Activity Entry)", expanded=len(all_activities) == 0):
        with st.form("form_add_activity", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                crop_dict = {"None": "सामान्य शेत काम / कोणतेही पीक नाही"}
                for cr in farmer_crops:
                    crop_dict[cr.id] = f"{cr.name} ({cr.variety or 'General'})"
                crop_sel = st.selectbox(
                    "🌾 संबंधित पीक निवडा (Select Crop)",
                    options=list(crop_dict.keys()),
                    format_func=lambda k: crop_dict[k],
                )
                act_type_sel = st.selectbox("कृतीचा प्रकार (Activity Type) *", options=ACTIVITY_TYPES)
                act_date = st.date_input("तारीख (Date) *", value=date.today())

            with f2:
                cost = st.number_input("खर्च (रुपये ₹)", min_value=0.0, value=0.0, step=100.0)
                desc = st.text_area("तपशील / शेरा (Details / Notes)", placeholder="उदा. १० मजूर लावून तण काढले व युरियाची दुसरी मात्रा दिली.")

            submitted = st.form_submit_button("✅ कृती जतन करा (Save Activity)", use_container_width=True)

            if submitted:
                try:
                    with get_db() as db:
                        crop_id_val = crop_sel if crop_sel != "None" else None
                        clean_type = act_type_sel.split(" (")[0]
                        desc_text = desc.strip() if desc and desc.strip() else f"{clean_type} काम पूर्ण केले"
                        ActivityService.create_activity(
                            db=db,
                            farmer_id=farmer.id,
                            activity_in=ActivityCreate(
                                crop_id=crop_id_val,
                                activity_type=clean_type,
                                activity_date=act_date,
                                description=desc_text,
                                cost=cost if cost > 0 else None,
                            ),
                        )
                    st.success("कृती यशस्वीरीत्या नोंदवली गेली!" if lang == "mr" else "Farm activity recorded successfully!")
                    st.rerun()
                except ValidationError as e:
                    st.error(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error(f"❌ त्रुटी: {str(e)}" if lang == "mr" else f"❌ Error: {str(e)}")

    st.markdown("---")

    # Filter controls
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        filter_crop = st.selectbox(
            "पिकानुसार फिल्टर करा",
            options=["All"] + [c.name for c in farmer_crops],
        )
    with c_f2:
        filter_type = st.selectbox(
            "कृतीच्या प्रकारानुसार फिल्टर करा",
            options=["All"] + [at.split(" (")[0] for at in ACTIVITY_TYPES],
        )

    # Filter records
    filtered = all_activities
    if filter_crop != "All":
        filtered = [a for a in filtered if a.crop and a.crop.name == filter_crop]
    if filter_type != "All":
        filtered = [a for a in filtered if a.activity_type.lower() == filter_type.lower()]

    st.markdown(f"##### 📋 नोंदवलेल्या कृतींची यादी ({len(filtered)})")

    if not filtered:
        st.markdown(
            textwrap.dedent(f"""
            <div class="empty-state-box">
                <div class="empty-state-icon">📅</div>
                <h3 style="margin: 0; color: #1b5e20; font-weight: 800;">{t('empty_diary_title', lang)}</h3>
                <p style="color: #4b634b; font-size: 1.05rem; margin: 10px 0 20px 0;">{t('empty_diary_desc', lang)}</p>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )
    else:
        for act in filtered:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                with col1:
                    crop_name_tag = f"🌾 **{act.crop.name}** | " if act.crop else "🚜 **सामान्य शेतकाम** | "
                    cost_tag = f" • खर्च: **{format_inr(act.cost)}**" if act.cost else ""
                    st.markdown(f"{crop_name_tag}**{act.activity_type}** ({format_date(act.activity_date)}){cost_tag}")
                    if act.description:
                        st.caption(act.description)
                with col2:
                    if st.button("🗑️", key=f"del_diary_{act.id}", use_container_width=True):
                        with get_db() as db:
                            ActivityService.delete_activity(db, farmer.id, act.id)
                        st.rerun()
