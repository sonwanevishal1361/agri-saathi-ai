"""Farm Activity Diary UI page."""

from datetime import date
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

    st.title(f"📅 {t('farm_diary', lang)}")

    with get_db() as db:
        farmer_crops = CropService.list_crops(db, farmer.id)
        all_activities = ActivityService.list_activities(db, farmer.id, limit=200)

    # Top metrics
    tot_cost = sum(a.cost or 0.0 for a in all_activities)
    m1, m2 = st.columns(2)
    with m1:
        st.metric("एकूण नोंदवलेल्या कृती (Total Activities)", len(all_activities))
    with m2:
        st.metric("कृतींशी संबंधित खर्च (Activity Costs)", format_inr(tot_cost))

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

            submitted = st.form_submit_button("✅ कृती जतन करा", use_container_width=True)

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
            f"""
            <div class="empty-state-box">
                <div class="empty-state-icon">📅</div>
                <h4 style="margin: 0; color: #1b5e20;">{t('empty_diary_title', lang)}</h4>
                <p style="color: #4b634b; font-size: 0.95rem; margin: 8px 0 0 0;">{t('empty_diary_desc', lang)}</p>
            </div>
            """,
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
                    if st.button("🗑️", key=f"del_diary_{act.id}"):
                        with get_db() as db:
                            ActivityService.delete_activity(db, farmer.id, act.id)
                        st.rerun()

