"""Crop Detail page showing timelines, activities, expenses, and harvests."""

from datetime import date
import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.activity_service import ActivityService
from services.expense_service import ExpenseService
from services.harvest_service import HarvestService
from schemas.activity import ActivityCreate
from schemas.expense import ExpenseCreate
from schemas.harvest import HarvestCreate
from schemas.crop import CropUpdate
from utils.formatting import format_inr, format_date
from ui.state import set_page
from core.exceptions import NotFoundError, AuthorizationError, ValidationError


ACTIVITY_TYPES = [
    "Sowing (पेरणी)",
    "Weeding / Hoeing (खुरपणी / कोळपणी)",
    "Fertilizer Application (खत देणे)",
    "Pesticide / Fungicide Spraying (औषध फवारणी)",
    "Irrigation (पाणी देणे)",
    "Pruning / Staking (छाटणी / आधार देणे)",
    "Harvesting / Picking (तोडणी / काढणी)",
    "Post-Harvest / Grading (प्रतवारी / साठवण)",
    "Other (इतर)",
]

EXPENSE_CATEGORIES = [
    "Seeds (बियाणे)",
    "Fertilizers (खते)",
    "Pesticides / Insecticides (कीटकनाशके)",
    "Labor / Wages (मजुरी)",
    "Machinery / Tractor Rental (ट्रॅक्टर / यंत्रे)",
    "Diesel / Fuel (इंधन)",
    "Irrigation / Electricity (पाणी / वीज)",
    "Transport / Mandi Hamali (वाहतूक / हमाली)",
    "Other (इतर)",
]


def render_crop_detail(farmer: AuthenticatedFarmer, crop_id: str):
    """Render comprehensive crop details and related records."""
    if not crop_id:
        st.warning("कोणतेही पीक निवडलेले नाही.")
        if st.button("⬅️ पिकांच्या यादीकडे परत जा"):
            set_page("crops")
            st.rerun()
        return

    with get_db() as db:
        try:
            crop = CropService.get_crop(db, farmer.id, crop_id)
        except (NotFoundError, AuthorizationError):
            st.error("पीक सापडले नाही किंवा आपल्याला या पिकात प्रवेश करण्याची परवानगी नाही.")
            if st.button("⬅️ मागे जा"):
                set_page("crops")
                st.rerun()
            return

        activities = ActivityService.list_activities(db, farmer.id, crop_id=crop.id)
        expenses = ExpenseService.list_expenses(db, farmer.id, crop_id=crop.id)
        harvests = HarvestService.list_harvest_records(db, farmer.id, crop_id=crop.id)
        crop_expenses_sum = ExpenseService.get_expense_summary(db, farmer.id, crop_id=crop.id)
        crop_harvest_sum = HarvestService.get_harvest_summary(db, farmer.id, crop_id=crop.id)

    # Top action bar
    top_col1, top_col2 = st.columns([4, 2])
    with top_col1:
        if st.button("⬅️ सर्व पिकांची यादी (All Crops)", key="btn_back_to_crops"):
            set_page("crops")
            st.rerun()
    with top_col2:
        if st.button("🤖 या पिकाबद्दल AI ला विचारा", key="btn_chat_this_crop", use_container_width=True):
            st.session_state["chat_crop_filter"] = crop.id
            set_page("chat")
            st.rerun()

    # Crop Title Card
    st.markdown(
        f"""
        <div style="background: #f1f8e9; border: 1px solid #c8e6c9; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="color: #1b5e20; margin: 0;">🌾 {crop.name} <span style="font-size: 1.1rem; color: #555;">({crop.variety or 'साधारण वाण'})</span></h2>
                    <p style="margin: 5px 0 0 0; color: #444;">
                        <strong>शेत/गट:</strong> {crop.plot_name or 'मुख्य शेत'} | <strong>क्षेत्र:</strong> {crop.area} {crop.area_unit} | <strong>माती:</strong> {crop.soil_type or 'N/A'}
                    </p>
                </div>
                <div style="text-align: right;">
                    <span style="background: #2e7d32; color: white; padding: 6px 14px; border-radius: 20px; font-weight: bold;">
                        {crop.status.upper()}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("सध्याची वाढीची अवस्था", crop.growth_stage)
    with m2:
        st.metric("पेरणी तारीख", format_date(crop.sowing_date))
    with m3:
        tot_exp = crop_expenses_sum.get("total_expense", 0.0)
        st.metric("एकूण लागलेला खर्च", format_inr(tot_exp))
    with m4:
        tot_rev = crop_harvest_sum.get("total_revenue", 0.0)
        st.metric("उत्पन्न (काढणी)", format_inr(tot_rev))

    st.markdown("---")

    # Update Stage & Status Expander
    with st.expander("⚙️ पिकाची अवस्था किंवा स्थिती बदला (Update Crop Stage / Status)"):
        with st.form("update_crop_form"):
            u1, u2 = st.columns(2)
            with u1:
                new_stage = st.text_input("नवीन अवस्था (Growth Stage)", value=crop.growth_stage)
            with u2:
                new_status = st.selectbox("स्थिती (Status)", options=["active", "harvested", "failed"], index=0 if crop.status == "active" else 1)
            up_submitted = st.form_submit_button("बदल जतन करा")
            if up_submitted:
                with get_db() as db:
                    CropService.update_crop(db, farmer.id, crop.id, CropUpdate(growth_stage=new_stage, status=new_status))
                st.success("पिकाची स्थिती अद्ययावत केली!")
                st.rerun()

    # Sub-tabs for Activities, Expenses, Harvest
    tab_acts, tab_exp, tab_harv = st.tabs([
        f"📅 दैनंदिनी नोंदी (Activities) [{len(activities)}]",
        f"💸 खर्च नोंदी (Expenses) [{len(expenses)}]",
        f"🌾 काढणी व उत्पन्न (Harvest) [{len(harvests)}]",
    ])

    # ---------------- TAB 1: ACTIVITIES ----------------
    with tab_acts:
        with st.expander("➕ या पिकासाठी नवीन कृती नोंदवा"):
            with st.form("form_add_crop_act", clear_on_submit=True):
                a1, a2 = st.columns(2)
                with a1:
                    act_type_sel = st.selectbox("कृतीचा प्रकार", options=ACTIVITY_TYPES)
                    act_date = st.date_input("तारीख", value=date.today())
                with a2:
                    act_cost = st.number_input("खर्च (रुपये)", min_value=0.0, value=0.0, step=100.0)
                    act_desc = st.text_area("तपशील / शेरा", placeholder="उदा. निंबोळी अर्क ५% फवारणी केली")
                if st.form_submit_button("नोंद जोडा"):
                    try:
                        clean_type = act_type_sel.split(" (")[0]
                        desc_text = act_desc.strip() if act_desc and act_desc.strip() else f"{clean_type} काम पूर्ण केले"
                        with get_db() as db:
                            ActivityService.create_activity(
                                db=db,
                                farmer_id=farmer.id,
                                activity_in=ActivityCreate(
                                    crop_id=crop.id,
                                    activity_type=clean_type,
                                    activity_date=act_date,
                                    cost=act_cost if act_cost > 0 else None,
                                    description=desc_text,
                                ),
                            )
                        st.success("कृती यशस्वीरीत्या नोंदवली!")
                        st.rerun()
                    except ValidationError as e:
                        st.error(f"⚠️ {str(e)}")
                    except Exception as e:
                        st.error(f"❌ त्रुटी: {str(e)}")

        if not activities:
            st.info("या पिकासाठी अद्याप कोणतीही कृती नोंदवलेली नाही.")
        else:
            for act in activities:
                with st.container(border=True):
                    c_act1, c_act2 = st.columns([4, 1])
                    with c_act1:
                        cost_str = f" • खर्च: **{format_inr(act.cost)}**" if act.cost else ""
                        st.markdown(f"**{act.activity_type}** ({format_date(act.activity_date)}){cost_str}")
                        if act.description:
                            st.caption(act.description)
                    with c_act2:
                        if st.button("🗑️", key=f"del_act_{act.id}"):
                            with get_db() as db:
                                ActivityService.delete_activity(db, farmer.id, act.id)
                            st.rerun()

    # ---------------- TAB 2: EXPENSES ----------------
    with tab_exp:
        with st.expander("➕ या पिकासाठी खर्च नोंदवा"):
            with st.form("form_add_crop_exp", clear_on_submit=True):
                e1, e2 = st.columns(2)
                with e1:
                    cat_sel = st.selectbox("खर्चाचा वर्ग (Category)", options=EXPENSE_CATEGORIES)
                    amount = st.number_input("रक्कम (₹) *", min_value=1.0, value=500.0, step=100.0)
                    exp_date = st.date_input("खर्चाची तारीख", value=date.today())
                with e2:
                    pay_method = st.selectbox("पेमेंट पद्धत", options=["Cash (रोख)", "UPI / Online", "Bank Transfer", "Credit / Udhari (उधारी)"])
                    payee = st.text_input("दुकानदार / व्यक्तीचे नाव", placeholder="उदा. कृषी सेवा केंद्र")
                    exp_notes = st.text_input("तपशील / बिल क्रमांक", placeholder="उदा. १० किलो बियाणे")

                if st.form_submit_button("खर्च जतन करा"):
                    try:
                        clean_cat = cat_sel.split(" (")[0]
                        desc_text = exp_notes.strip() if exp_notes and exp_notes.strip() else f"{clean_cat} खर्च"
                        with get_db() as db:
                            ExpenseService.create_expense(
                                db=db,
                                farmer_id=farmer.id,
                                expense_in=ExpenseCreate(
                                    crop_id=crop.id,
                                    category=clean_cat,
                                    amount=amount,
                                    expense_date=exp_date,
                                    description=desc_text,
                                    vendor=payee.strip() if payee and payee.strip() else None,
                                    payment_method=pay_method.split(" (")[0],
                                ),
                            )
                        st.success("खर्च यशस्वीरीत्या नोंदवला!")
                        st.rerun()
                    except ValidationError as e:
                        st.error(f"⚠️ {str(e)}")
                    except Exception as e:
                        st.error(f"❌ त्रुटी: {str(e)}")

        if not expenses:
            st.info("या पिकासाठी कोणताही खर्च नोंदवलेला नाही.")
        else:
            for exp in expenses:
                with st.container(border=True):
                    e_col1, e_col2 = st.columns([4, 1])
                    with e_col1:
                        st.markdown(f"**{exp.category}: {format_inr(exp.amount)}** ({format_date(exp.expense_date)})")
                        st.caption(f"दुकान/व्यक्ती: {exp.vendor or exp.payee or 'N/A'} | तपशील: {exp.description or exp.notes or '-'}")
                    with e_col2:
                        if st.button("🗑️", key=f"del_exp_{exp.id}"):
                            with get_db() as db:
                                ExpenseService.delete_expense(db, farmer.id, exp.id)
                            st.rerun()

    # ---------------- TAB 3: HARVEST ----------------
    with tab_harv:
        with st.expander("➕ काढणी व विक्री नोंदवा (Record Harvest)"):
            with st.form("form_add_crop_harv", clear_on_submit=True):
                h1, h2 = st.columns(2)
                with h1:
                    h_date = st.date_input("काढणी तारीख", value=date.today())
                    quantity = st.number_input("उत्पादन प्रमाण (Quantity) *", min_value=0.1, value=10.0, step=1.0)
                    h_unit = st.selectbox("एकक (Unit)", options=["Quintal (क्विंटल)", "Kg (किलो)", "Tonne (टन)", "Crates / Bags"])
                with h2:
                    rate = st.number_input("दर प्रति एकक (Rate per unit ₹) *", min_value=1.0, value=6500.0, step=100.0)
                    buyer = st.text_input("खरेदीदार / व्यापारी / APMC", placeholder="उदा. बारामती APMC / व्यापारी नाव")
                    h_quality = st.selectbox("प्रत (Quality)", options=["A Grade (उत्कृष्ट)", "B Grade (मध्यम)", "C Grade"])

                if st.form_submit_button("काढणी जतन करा"):
                    try:
                        clean_unit = h_unit.split(" (")[0]
                        clean_grade = h_quality.split(" (")[0]
                        with get_db() as db:
                            HarvestService.create_harvest(
                                db=db,
                                farmer_id=farmer.id,
                                harvest_in=HarvestCreate(
                                    crop_id=crop.id,
                                    harvest_date=h_date,
                                    quantity=quantity,
                                    quantity_unit=clean_unit,
                                    selling_price=rate,
                                    sale_quantity=quantity,
                                    buyer_name=buyer.strip() if buyer and buyer.strip() else None,
                                    quality_grade=clean_grade,
                                ),
                            )
                        st.success("काढणी व उत्पन्न यशस्वीरीत्या नोंदवले!")
                        st.rerun()
                    except ValidationError as e:
                        st.error(f"⚠️ {str(e)}")
                    except Exception as e:
                        st.error(f"❌ त्रुटी: {str(e)}")

        if not harvests:
            st.info("या पिकासाठी कोणतीही काढणी नोंदवलेली नाही.")
        else:
            for h in harvests:
                with st.container(border=True):
                    h_col1, h_col2 = st.columns([4, 1])
                    with h_col1:
                        st.markdown(f"**उत्पादन: {h.quantity} {h.unit} @ {format_inr(h.selling_price_per_unit)}/{h.unit}**")
                        st.markdown(f"एकूण महसूल: **{format_inr(h.total_revenue)}** | तारीख: {format_date(h.harvest_date)}")
                        st.caption(f"खरेदीदार: {h.buyer_name or 'स्थानिक बाजार'} | प्रत: {h.quality_grade or 'Standard'}")
                    with h_col2:
                        if st.button("🗑️", key=f"del_harv_{h.id}"):
                            with get_db() as db:
                                HarvestService.delete_harvest(db, farmer.id, h.id)
                            st.rerun()
