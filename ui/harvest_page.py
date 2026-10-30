"""Harvest and Revenue tracking UI page."""

from datetime import date
import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.harvest_service import HarvestService
from schemas.harvest import HarvestCreate
from utils.formatting import format_inr, format_date
from utils.language import t
from ui.state import get_language
from core.exceptions import ValidationError


def render_harvest_page(farmer: AuthenticatedFarmer):
    """Render harvest records and farm revenue page."""
    lang = get_language()

    st.title(f"🌾 {t('harvest', lang)} नोंदी व उत्पन्न (Harvest & Revenue)")

    with get_db() as db:
        farmer_crops = CropService.list_crops(db, farmer.id)
        all_harvests = HarvestService.list_harvest_records(db, farmer.id, limit=200)
        harvest_summary = HarvestService.get_harvest_summary(db, farmer.id)

    total_revenue = harvest_summary.get("total_revenue", 0.0)
    total_expense = harvest_summary.get("total_expenses", 0.0)
    net_profit = harvest_summary.get("net_profit", 0.0)

    # 3 Summary metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("एकूण काढणी उत्पन्न (Total Revenue)", format_inr(total_revenue))
    with m2:
        st.metric("एकूण लागलेला खर्च (Total Expenses)", format_inr(total_expense))
    with m3:
        st.metric(
            "निव्वळ नफा (Net Profit / Balance)",
            format_inr(net_profit),
            delta="नफा" if net_profit >= 0 else "-तोटा",
        )

    st.markdown("---")

    # Add Harvest Expander
    with st.expander("➕ नवीन काढणी व विक्री नोंदवा (Add Harvest Record)", expanded=len(all_harvests) == 0):
        if not farmer_crops:
            st.warning("काढणी नोंदवण्यासाठी प्रथम 'माझी पिके' मधून पीक जोडा.")
        else:
            with st.form("form_add_harvest", clear_on_submit=True):
                h1, h2 = st.columns(2)
                with h1:
                    crop_dict = {cr.id: f"{cr.name} ({cr.variety or 'General'})" for cr in farmer_crops}
                    crop_sel = st.selectbox(
                        "🌾 संबंधित पीक निवडा (Crop) *",
                        options=list(crop_dict.keys()),
                        format_func=lambda k: crop_dict[k],
                    )
                    h_date = st.date_input("काढणी / विक्री तारीख *", value=date.today())
                    quantity = st.number_input("उत्पादन प्रमाण (Quantity) *", min_value=0.1, value=15.0, step=1.0)

                with h2:
                    unit_sel = st.selectbox("एकक (Unit) *", options=["Quintal (क्विंटल)", "Kg (किलो)", "Tonne (टन)", "Crates / Bags"])
                    rate = st.number_input("विक्री दर प्रति एकक (Rate ₹) *", min_value=1.0, value=7200.0, step=100.0)
                    buyer = st.text_input("खरेदीदार / व्यापारी / बाजार समिती", placeholder="उदा. नाशिक APMC / व्यापारी नाव")
                    quality = st.selectbox("मालाची प्रत (Quality Grade)", options=["A Grade (उत्कृष्ट)", "B Grade (मध्यम)", "C Grade"])

                submitted = st.form_submit_button("✅ काढणी नोंद जतन करा", use_container_width=True)

                if submitted:
                    try:
                        clean_unit = unit_sel.split(" (")[0]
                        clean_grade = quality.split(" (")[0]
                        with get_db() as db:
                            HarvestService.create_harvest(
                                db=db,
                                farmer_id=farmer.id,
                                harvest_in=HarvestCreate(
                                    crop_id=crop_sel,
                                    harvest_date=h_date,
                                    quantity=quantity,
                                    quantity_unit=clean_unit,
                                    selling_price=rate,
                                    sale_quantity=quantity,
                                    buyer_name=buyer.strip() if buyer and buyer.strip() else None,
                                    quality_grade=clean_grade,
                                ),
                            )
                        st.success("काढणी नोंद यशस्वीरीत्या जतन केली!" if lang == "mr" else "Harvest record saved successfully!")
                        st.rerun()
                    except ValidationError as e:
                        st.error(f"⚠️ {str(e)}")
                    except Exception as e:
                        st.error(f"❌ त्रुटी: {str(e)}" if lang == "mr" else f"❌ Error: {str(e)}")

    st.markdown("---")

    st.markdown(f"##### 📦 विक्री व काढणी नोंदी ({len(all_harvests)})")

    if not all_harvests:
        st.markdown(
            f"""
            <div class="empty-state-box">
                <div class="empty-state-icon">💰</div>
                <h4 style="margin: 0; color: #1b5e20;">{t('empty_harvest_title', lang)}</h4>
                <p style="color: #4b634b; font-size: 0.95rem; margin: 8px 0 0 0;">{t('empty_harvest_desc', lang)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for harv in all_harvests:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                with col1:
                    crop_name_tag = f"🌾 **{harv.crop.name}** | " if harv.crop else ""
                    st.markdown(f"{crop_name_tag}उत्पादन: **{harv.quantity} {harv.unit}** @ {format_inr(harv.selling_price_per_unit)}/{harv.unit}")
                    st.markdown(f"एकूण विक्री उत्पन्न: **{format_inr(harv.total_revenue)}** (तारीख: {format_date(harv.harvest_date)})")
                    st.caption(f"खरेदीदार: {harv.buyer_name or 'स्थानिक बाजार'} | प्रत: {harv.quality_grade or 'Standard'}")
                with col2:
                    if st.button("🗑️", key=f"del_harv_page_{harv.id}"):
                        with get_db() as db:
                            HarvestService.delete_harvest_record(db, farmer.id, harv.id)
                        st.rerun()

