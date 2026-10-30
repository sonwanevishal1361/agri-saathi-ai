"""Farm Expenses UI page."""

from datetime import date
import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.expense_service import ExpenseService
from schemas.expense import ExpenseCreate
from utils.formatting import format_inr, format_date
from utils.language import t
from ui.state import get_language
from core.exceptions import ValidationError


EXPENSE_CATEGORIES = [
    "Seeds (बियाणे)",
    "Fertilizers (खते)",
    "Pesticides / Insecticides (कीटकनाशके)",
    "Labor / Wages (मजुरी)",
    "Machinery / Tractor Rental (ट्रॅक्टर / यंत्रे भाडे)",
    "Diesel / Fuel (डिझेल / इंधन)",
    "Irrigation / Electricity (सिंचन / वीजबिल)",
    "Transport / Mandi Hamali (वाहतूक / हमाली)",
    "Equipment & Tools (हत्यारे व अवजारे)",
    "Other (इतर)",
]


def render_expenses_page(farmer: AuthenticatedFarmer):
    """Render farm expense logging and financial summary page."""
    lang = get_language()

    st.title(f"💸 {t('expenses', lang)} (खर्च व्यवस्थापन)")

    with get_db() as db:
        farmer_crops = CropService.list_crops(db, farmer.id)
        all_expenses = ExpenseService.list_expenses(db, farmer.id, limit=300)
        expense_summary = ExpenseService.get_expense_summary(db, farmer.id)

    total_expense = expense_summary.get("total_expense", 0.0)
    by_category = expense_summary.get("by_category", {})

    # Top summary metrics
    m1, m2 = st.columns(2)
    with m1:
        st.metric("एकूण नोंदवलेला खर्च (Total Expenses)", format_inr(total_expense))
    with m2:
        top_cat = max(by_category.items(), key=lambda x: x[1])[0] if by_category else "N/A"
        st.metric("सर्वाधिक खर्च असलेला घटक (Top Category)", top_cat)

    st.markdown("---")

    # Add Expense Expander
    with st.expander("➕ नवीन खर्च नोंदवा (Add Farm Expense)", expanded=len(all_expenses) == 0):
        with st.form("form_add_expense", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                crop_dict = {"None": "सामान्य / सर्व पिकांसाठी एकत्रित खर्च"}
                for cr in farmer_crops:
                    crop_dict[cr.id] = f"{cr.name} ({cr.variety or 'General'})"
                crop_sel = st.selectbox(
                    "🌾 संबंधित पीक निवडा (Select Crop)",
                    options=list(crop_dict.keys()),
                    format_func=lambda k: crop_dict[k],
                )
                cat_sel = st.selectbox("खर्चाचा वर्ग (Category) *", options=EXPENSE_CATEGORIES)
                amount = st.number_input("खर्च रक्कम (Amount in ₹) *", min_value=1.0, value=1000.0, step=100.0)

            with f2:
                exp_date = st.date_input("खर्चाची तारीख (Date) *", value=date.today())
                pay_method = st.selectbox(
                    "पेमेंट पद्धत (Payment Method)",
                    options=["Cash (रोख)", "UPI / PhonePe / GPay", "Bank Transfer (NEFT/IMPS)", "Credit / Udhari (उधारी / बाकी)"],
                )
                payee = st.text_input("दुकानदार / मजुराचे नाव (Payee / Vendor)", placeholder="उदा. महालक्ष्मी कृषी केंद्र / बाळू मुकादम")
                notes = st.text_input("तपशील / बिल नंबर (Receipt / Bill Note)", placeholder="उदा. २ पोती १०:२६:२६ खत")

            submitted = st.form_submit_button("✅ खर्च जतन करा", use_container_width=True)

            if submitted:
                try:
                    with get_db() as db:
                        crop_id_val = crop_sel if crop_sel != "None" else None
                        desc_text = notes.strip() if notes and notes.strip() else f"{cat_sel.split(' (')[0]} खर्च"
                        ExpenseService.create_expense(
                            db=db,
                            farmer_id=farmer.id,
                            expense_in=ExpenseCreate(
                                crop_id=crop_id_val,
                                category=cat_sel.split(" (")[0],
                                amount=amount,
                                expense_date=exp_date,
                                description=desc_text,
                                vendor=payee.strip() if payee and payee.strip() else None,
                                payment_method=pay_method.split(" (")[0],
                            ),
                        )
                    st.success(f"खर्च यशस्वीरीत्या नोंदवला: {format_inr(amount)}" if lang == "mr" else f"Expense saved successfully: {format_inr(amount)}")
                    st.rerun()
                except ValidationError as e:
                    st.error(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error(f"❌ त्रुटी: {str(e)}" if lang == "mr" else f"❌ Error: {str(e)}")

    st.markdown("---")

    # Category breakdown visualization
    if by_category:
        st.markdown("##### 📊 वर्गवारीनुसार खर्चाचे प्रमाण (Expense Category Breakdown)")
        cat_cols = st.columns(min(len(by_category), 4))
        for idx, (cat_name, cat_amt) in enumerate(sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:4]):
            col_idx = idx % 4
            with cat_cols[col_idx]:
                pct = (cat_amt / total_expense * 100) if total_expense > 0 else 0
                st.metric(label=f"🏷️ {cat_name}", value=format_inr(cat_amt), delta=f"{pct:.1f}%")

    st.markdown("---")

    # Filter controls
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        filter_crop = st.selectbox(
            "पिकानुसार फिल्टर",
            options=["All"] + [c.name for c in farmer_crops],
        )
    with c_f2:
        filter_cat = st.selectbox(
            "खर्चाच्या वर्गानुसार फिल्टर",
            options=["All"] + [c.split(" (")[0] for c in EXPENSE_CATEGORIES],
        )

    # Filter records
    filtered = all_expenses
    if filter_crop != "All":
        filtered = [e for e in filtered if e.crop and e.crop.name == filter_crop]
    if filter_cat != "All":
        filtered = [e for e in filtered if e.category.lower() == filter_cat.lower()]

    st.markdown(f"##### 🧾 खर्चाची नोंदवही ({len(filtered)})")

    if not filtered:
        st.markdown(
            f"""
            <div class="empty-state-box">
                <div class="empty-state-icon">💸</div>
                <h4 style="margin: 0; color: #1b5e20;">{t('empty_expenses_title', lang)}</h4>
                <p style="color: #4b634b; font-size: 0.95rem; margin: 8px 0 0 0;">{t('empty_expenses_desc', lang)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for exp in filtered:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                with col1:
                    crop_name_tag = f"🌾 **{exp.crop.name}** | " if exp.crop else "🚜 **सामान्य खर्च** | "
                    st.markdown(f"{crop_name_tag}**{exp.category}: {format_inr(exp.amount)}** ({format_date(exp.expense_date)})")
                    st.caption(f"दुकान/व्यक्ती: {exp.vendor or exp.payee or 'N/A'} | तपशील: {exp.description or exp.notes or '-'}")
                with col2:
                    if st.button("🗑️", key=f"del_exp_page_{exp.id}"):
                        with get_db() as db:
                            ExpenseService.delete_expense(db, farmer.id, exp.id)
                        st.rerun()

