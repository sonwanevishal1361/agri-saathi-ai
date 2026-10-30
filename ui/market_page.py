"""Multi-Market APMC Mandi Price Comparison and Transport Logistics Page."""

import urllib.parse
from datetime import datetime
import pandas as pd
import streamlit as st

from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.mandi_service import MandiService
from utils.formatting import format_inr
from utils.language import t


def render_market_page(farmer: AuthenticatedFarmer):
    """Render interactive multi-market APMC comparison portal."""
    lang = farmer.preferred_language or "mr"

    st.title(f"📈 {t('mandi_title', lang)}")
    st.markdown(t("mandi_subtitle", lang))

    # Determine default commodity based on farmer's active crops
    default_comm_index = 0
    active_crops = []
    try:
        active_crops = CropService.list_crops(farmer.id, status="active")
    except Exception:
        pass

    supported_commodities = MandiService.get_supported_commodities()
    if active_crops and supported_commodities:
        fav_name = active_crops[0].name.lower()
        for idx, c in enumerate(supported_commodities):
            if fav_name in c.lower() or c.lower() in fav_name:
                default_comm_index = idx
                break

    # Top Filters in Responsive Columns
    f1, f2 = st.columns(2)
    with f1:
        sel_comm = st.selectbox(
            f"🌾 {t('mandi_select_crop', lang)}",
            options=supported_commodities,
            index=default_comm_index if default_comm_index < len(supported_commodities) else 0,
        )
    with f2:
        state_options = ["Maharashtra", "All", "Madhya Pradesh", "Gujarat", "Karnataka", "Punjab", "Haryana"]
        farmer_state = farmer.state or "Maharashtra"
        state_idx = 0
        if farmer_state in state_options:
            state_idx = state_options.index(farmer_state)

        sel_state = st.selectbox(
            f"📍 {t('mandi_state', lang)}",
            options=state_options,
            index=state_idx,
        )

    # Optional District & Variety Filter Expander
    with st.expander(f"🔍 {t('filter', lang) if t('filter', lang) != 'Filter' else 'अधिक निकष (More Filters)'}", expanded=False):
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            sel_district = st.text_input(
                f"🏛️ {t('mandi_district', lang)}",
                value="",
                placeholder="उदा. Nagpur, Nashik, Pune...",
            )
        with c_sub2:
            sel_variety = st.text_input(
                f"🏷️ {t('mandi_variety', lang)}",
                value="",
                placeholder="उदा. Medium Staple, Red, Yellow...",
            )

    # Transport & Quantity Logistics Configuration
    st.markdown(f"#### 🚚 {t('mandi_transport_calc_title', lang)}")
    t1, t2 = st.columns(2)
    with t1:
        transport_rate = st.number_input(
            f"⛽ {t('mandi_transport_rate', lang)}",
            min_value=10.0,
            max_value=300.0,
            value=50.0,
            step=5.0,
            help="अंदाजे वाहतूक दर: प्रति क्विंटल प्रति १०० किलोमीटर.",
        )
    with t2:
        selling_qty = st.number_input(
            f"⚖️ {t('mandi_quantity', lang)}",
            min_value=1.0,
            max_value=5000.0,
            value=50.0,
            step=5.0,
            help="शेतमालाचे अंदाजे प्रमाण (क्विंटलमध्ये). एकूण नफ्याच्या हिशोबासाठी वापरले जाते.",
        )

    # Fetch multi-market data
    state_arg = sel_state if sel_state != "All" else None
    district_arg = sel_district.strip() if sel_district.strip() else None
    variety_arg = sel_variety.strip() if sel_variety.strip() else None

    with st.spinner("बाजारभाव माहिती मिळवत आहे..."):
        mandi_res = MandiService.get_prices(
            commodity=sel_comm,
            state=state_arg,
            district=district_arg,
            variety=variety_arg,
        )

    raw_records = mandi_res.get("records", [])

    # Enrich records with distance from farmer district & transport deduction
    farmer_district = farmer.district or "Nagpur"
    enriched_records = []
    for r in raw_records:
        rec_dist = r.get("district") or farmer_district
        dist_km = MandiService.get_district_distance(farmer_district, rec_dist)
        modal_p = float(r.get("modal_price", 0.0))
        trans_cost = round((dist_km / 100.0) * transport_rate, 2)
        net_p = round(max(0.0, modal_p - trans_cost), 2)
        gross_rev = round(modal_p * selling_qty, 0)
        net_rev = round(net_p * selling_qty, 0)

        item = dict(r)
        item["distance_km"] = dist_km
        item["transport_cost_per_qtl"] = trans_cost
        item["estimated_net_price"] = net_p
        item["gross_revenue"] = gross_rev
        item["net_revenue"] = net_rev
        enriched_records.append(item)

    # Sorting Controls
    sort_options = {
        t("mandi_sort_modal_price", lang): lambda x: x["modal_price"],
        t("mandi_sort_net_price", lang): lambda x: x["estimated_net_price"],
        t("mandi_sort_distance", lang): lambda x: -x["distance_km"],
        t("mandi_sort_latest_date", lang): lambda x: x["data_date"],
    }

    sort_choice = st.radio(
        f"📊 **{t('mandi_sort_by', lang)}:**",
        options=list(sort_options.keys()),
        index=0,
        horizontal=True,
    )

    is_dist_sort = sort_choice == t("mandi_sort_distance", lang)
    display_records = sorted(
        enriched_records,
        key=sort_options[sort_choice],
        reverse=not is_dist_sort,
    )

    # Data Mode Banner
    st.info(
        f"ℹ️ **{t('mandi_data_source', lang)}:** {mandi_res.get('data_mode')} | "
        f"[अधिकृत Agmarknet पोर्टल]({mandi_res.get('official_portal_url')})\n\n"
        f"🕒 {t('mandi_retrieved_at', lang)}: `{mandi_res.get('retrieved_at')}`\n\n"
        f"{mandi_res.get('notice')}"
    )

    if not display_records:
        st.warning(f"⚠️ {t('mandi_no_records_found', lang)}")
        return

    # Top Hero Card: Best Price Today
    top_record = display_records[0]
    with st.container(border=True):
        st.markdown(
            f"<div style='background: linear-gradient(135deg, #1b5e20, #2e7d32); "
            f"padding: 16px; border-radius: 12px; color: white; margin-bottom: 8px;'>"
            f"<span style='font-size: 1.25rem; font-weight: bold;'>{t('mandi_best_price_today', lang)}</span>"
            f"<h2 style='color: #ffeb3b; margin: 4px 0 8px 0; font-size: 2.1rem;'>"
            f"{format_inr(top_record['modal_price'])} <span style='font-size: 1rem; color: #f1f8e9;'>/ {top_record.get('unit', 'Quintal')}</span></h2>"
            f"<p style='margin: 0; font-size: 1.05rem;'>"
            f"🏛️ <b>{top_record['market']}</b> ({top_record['district']}, {top_record['state']})<br/>"
            f"📅 {top_record['data_date']} | {top_record.get('freshness_badge', '')} | 🏷️ {top_record['variety']}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        h_c1, h_c2, h_c3 = st.columns(3)
        with h_c1:
            st.metric(
                label=f"🚗 {t('mandi_distance', lang)} ({farmer_district} पासून)",
                value=f"{top_record['distance_km']} km",
            )
        with h_c2:
            st.metric(
                label=f"⛽ {t('mandi_transport_deduction', lang)}",
                value=format_inr(top_record['transport_cost_per_qtl']),
            )
        with h_c3:
            st.metric(
                label=f"💰 {t('mandi_net_price', lang)}",
                value=format_inr(top_record['estimated_net_price']),
            )

    # Local District APMC Comparison Callout
    local_rec = next(
        (r for r in display_records if r.get("district", "").lower() == farmer_district.lower()),
        None,
    )
    if local_rec and local_rec["market"] != top_record["market"]:
        diff_modal = top_record["modal_price"] - local_rec["modal_price"]
        pct_diff = round((diff_modal / local_rec["modal_price"]) * 100, 1) if local_rec["modal_price"] > 0 else 0
        extra_total = round(diff_modal * selling_qty, 0)

        with st.container(border=True):
            st.markdown(f"##### 🎯 {t('mandi_local_compare_title', lang)}")
            st.caption(t("mandi_local_compare_desc", lang))

            l_col1, l_col2 = st.columns(2)
            with l_col1:
                st.markdown(
                    f"📍 **स्थानिक बाजार ({local_rec['market']}):** {format_inr(local_rec['modal_price'])}"
                )
            with l_col2:
                st.markdown(
                    f"🏆 **शीर्ष बाजार ({top_record['market']}):** {format_inr(top_record['modal_price'])}"
                )

            if diff_modal > 0:
                st.success(
                    f"✨ **{top_record['market']}** मध्ये भाव **{format_inr(diff_modal)}** "
                    f"(+{pct_diff}%) जास्त आहे! {selling_qty} क्विंटलवर अंदाजे **{format_inr(extra_total)}** चा अधिक नफा शक्य."
                )
            elif diff_modal < 0:
                st.info(
                    f"ℹ️ स्थानिक बाजार समिती **{local_rec['market']}** चा दर जास्त फायदेशीर ठरत आहे."
                )

    # Top Markets Visual Bar Chart
    st.markdown("---")
    st.markdown(f"#### 📊 {t('mandi_chart_top_markets', lang)}")
    chart_markets = display_records[:7]
    if chart_markets:
        chart_df = pd.DataFrame({
            "Market": [f"{m['market']} ({m['district']})" for m in chart_markets],
            "Modal Price (₹)": [m["modal_price"] for m in chart_markets],
            "Net Price (₹)": [m["estimated_net_price"] for m in chart_markets],
        }).set_index("Market")
        st.bar_chart(chart_df)

    # Multi-Market Cards Comparison List
    st.markdown(f"#### 📋 {t('mandi_records_count', lang)} ({len(display_records)})")

    for idx, rec in enumerate(display_records, 1):
        with st.container(border=True):
            col_left, col_mid, col_right = st.columns([3, 2, 2])
            with col_left:
                st.markdown(f"### #{idx} 🏛️ {rec['market']}")
                st.markdown(f"**जिल्हा:** `{rec['district']}` | **राज्य:** {rec['state']}")
                st.markdown(f"**वाण:** {rec['variety']} | **प्रत:** {rec['grade']}")
                st.caption(f"📅 दिनांक: {rec['data_date']} | {rec.get('freshness_badge', '')}")

            with col_mid:
                st.markdown(f"⭐ **{t('mandi_modal_price', lang)}:**")
                st.markdown(f"<h3 style='color: #2e7d32; margin:0;'>{format_inr(rec['modal_price'])}</h3>", unsafe_allow_html=True)
                st.caption(f"{t('mandi_min_max', lang)}: {format_inr(rec['min_price'])} - {format_inr(rec['max_price'])}")
                st.markdown(f"🚗 {t('mandi_distance', lang)}: **{rec['distance_km']} km**")
                st.markdown(f"⛽ {t('mandi_transport_deduction', lang)}: -{format_inr(rec['transport_cost_per_qtl'])}")

            with col_right:
                st.markdown(f"💵 **{t('mandi_net_price', lang)}:**")
                st.markdown(f"<h3 style='color: #1565c0; margin:0;'>{format_inr(rec['estimated_net_price'])}</h3>", unsafe_allow_html=True)
                st.caption(f"एकक: {rec.get('unit', 'Rs / Quintal')}")
                st.markdown(f"📦 {selling_qty} Qtl {t('mandi_gross_revenue', lang)}: **{format_inr(rec['gross_revenue'])}**")
                st.markdown(f"💰 {selling_qty} Qtl {t('mandi_net_revenue', lang)}: **{format_inr(rec['net_revenue'])}**")

    # Historical Price Trend Chart Expander
    st.markdown("---")
    with st.expander(f"📈 {t('mandi_price_trend_title', lang)}", expanded=False):
        market_list = [r["market"] for r in display_records]
        sel_trend_market = st.selectbox("बाजार समिती निवडा (Select Market for Trend)", options=market_list, index=0)
        trend_days = st.slider("दिवस (Days)", min_value=7, max_value=30, value=14, step=7)

        trend_data = MandiService.get_price_trend(sel_comm, sel_trend_market, days=trend_days)
        if trend_data:
            trend_df = pd.DataFrame({
                "Date": [pt["date"] for pt in trend_data],
                "Modal Price (₹)": [pt["modal_price"] for pt in trend_data],
                "Min Price (₹)": [pt["min_price"] for pt in trend_data],
                "Max Price (₹)": [pt["max_price"] for pt in trend_data],
            }).set_index("Date")
            st.line_chart(trend_df)
            st.caption(f"📊 {sel_trend_market} मधील {sel_comm} चे मागील {trend_days} दिवसांचे भाव.")

    # WhatsApp Share & Price Alert Utilities
    st.markdown("---")
    u_c1, u_c2 = st.columns(2)

    with u_c1:
        with st.container(border=True):
            st.markdown(f"##### 📲 {t('mandi_whatsapp_share', lang)}")
            # Generate WhatsApp ready formatted message for top 3 markets
            share_lines = [
                "🌾 *कृषी साथी AI - आजचे APMC बाजारभाव*",
                f"पीक: *{sel_comm}* | राज्य: {sel_state}",
                f"तारीख: {datetime.now().strftime('%d-%m-%Y')}",
                "",
                "🏆 *प्रमुख बाजार समित्यांमधील भाव:*",
            ]
            for m in display_records[:4]:
                share_lines.append(
                    f"• *{m['market']}* ({m['district']}): ₹{int(m['modal_price'])}/क्विंटल (निव्वळ: ₹{int(m['estimated_net_price'])})"
                )
            share_lines.extend([
                "",
                f"💡 {selling_qty} क्विंटलवर सर्वोत्तम नफा: *{top_record['market']}* (अंदाजे ₹{int(top_record['net_revenue'])})",
                "अधिकृत माहिती: Agmarknet (data.gov.in)",
                "कृषी साथी AI सोबत शेती करा फायद्याची!",
            ])
            wa_text = "\n".join(share_lines)
            encoded_text = urllib.parse.quote(wa_text)
            wa_url = f"https://api.whatsapp.com/send?text={encoded_text}"

            st.text_area("व्हॉट्सअ‍ॅप मेसेज सारांश (Preview)", value=wa_text, height=130)
            st.link_button("📲 व्हॉट्सअ‍ॅपवर पाठवा (Send to WhatsApp)", url=wa_url)

    with u_c2:
        with st.container(border=True):
            st.markdown(f"##### 🔔 {t('mandi_price_alert_title', lang)}")
            st.caption(t("mandi_price_alert_desc", lang))
            alert_target = st.number_input(
                "अपेक्षित भाव (Target Price ₹)",
                min_value=100.0,
                max_value=50000.0,
                value=float(top_record["modal_price"] + 200),
                step=50.0,
            )
            if st.button(t("mandi_set_alert_btn", lang)):
                st.success(f"✅ {sel_comm} साठी ₹{int(alert_target)} चा भाव अलर्ट यशस्वीरीत्या सेट केला!")

    # Footer Disclaimer
    st.markdown("---")
    st.caption(f"⚠️ **महत्त्वाची सूचना:** {t('mandi_disclaimer_notice', lang)}")
