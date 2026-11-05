"""Developer Admin Panel and Data Management Interface for AgriSaathi AI.

Provides platform monitoring, farmer management, agricultural analytics,
sanitized CSV/Excel/JSON data exports, database backup & restore, and audit logging.
Strictly restricted to users with role="admin".
"""

import textwrap
import streamlit as st

from core.database import get_db, get_database_info
from core.auth import AuthenticatedFarmer, require_admin
from core.exceptions import AuthorizationError
from services.admin_service import AdminService
from services.backup_service import BackupService
from utils.formatting import format_inr
from utils.logging_config import logger
from ui.state import set_page, logout


def render_admin_page(admin: AuthenticatedFarmer):
    """Render the comprehensive developer admin panel and data management dashboard."""
    try:
        require_admin(admin)
    except AuthorizationError as e:
        st.error(f"⛔ {e.message}")
        st.stop()

    # ---------------- ADMIN TOP BAR & ACTION BUTTONS ----------------
    top_nav_c1, top_nav_c2 = st.columns([3, 1])
    with top_nav_c1:
        st.caption("🛡️ ENTERPRISE PLATFORM GOVERNANCE & TELEMETRY")
    with top_nav_c2:
        btn_exit_c, btn_out_c = st.columns(2)
        with btn_exit_c:
            if st.button("🏠 Farmer App", key="admin_exit_to_farmer_btn", use_container_width=True, type="secondary"):
                set_page("dashboard")
                st.rerun()
        with btn_out_c:
            if st.button("🚪 Logout", key="admin_top_logout_btn", use_container_width=True):
                logout()
                st.rerun()

    # ---------------- ADMIN HEADER ----------------
    admin_hdr_html = textwrap.dedent(f"""
        <div style="
            background: linear-gradient(135deg, #07190f 0%, #0d281a 45%, #153e28 100%);
            color: white;
            border-radius: 22px;
            padding: 22px 26px;
            margin-bottom: 20px;
            box-shadow: 0 16px 36px -8px rgba(7, 25, 15, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(134, 239, 172, 0.2);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 52px; height: 52px; border-radius: 14px; background: rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: center; font-size: 1.8rem; border: 1px solid rgba(255, 255, 255, 0.2);">
                        🛠️
                    </div>
                    <div>
                        <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; color: #86efac; text-transform: uppercase;">
                            Control Center • Enterprise Edition
                        </div>
                        <h2 style="margin: 2px 0 0 0; color: #ffffff; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.01em;">
                            AgriSaathi AI — Platform Command Center
                        </h2>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="background: rgba(255,255,255,0.14); padding: 6px 14px; border-radius: 20px; font-size: 0.86rem; font-weight: 700; color: #ffffff; border: 1px solid rgba(255,255,255,0.25);">
                        👤 Admin: <strong>{admin.full_name}</strong>
                    </span>
                    <span style="background: #e8f5e9; color: #0b2316; padding: 6px 14px; border-radius: 20px; font-size: 0.86rem; font-weight: 800;">
                        🛡️ SUPERUSER
                    </span>
                </div>
            </div>
        </div>
    """).strip()
    st.markdown(admin_hdr_html, unsafe_allow_html=True)

    # 9 Administrative Sections via Segmented Control
    admin_nav_opts = [
        "📊 Overview",
        "👥 Farmers",
        "🌾 Crop Analytics",
        "🚜 Activities",
        "💰 Financial Health",
        "🤖 AI Usage",
        "📥 Data Exports",
        "🛡️ Backup & Maintenance",
        "📜 Audit Logs",
    ]

    admin_section = st.segmented_control(
        "Admin Navigation",
        options=admin_nav_opts,
        default="📊 Overview",
        key="admin_segmented_nav",
        label_visibility="collapsed",
    )
    if not admin_section:
        admin_section = "📊 Overview"

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 1: OVERVIEW
    # =========================================================================
    if admin_section == "📊 Overview":
        st.subheader("📊 Platform Health & System Overview")
        try:
            with get_db() as db:
                overview = AdminService.get_system_overview(db, admin)
        except Exception as e:
            logger.exception("Failed to load platform overview: %s", e)
            st.warning("⚠️ System overview metrics are temporarily unavailable. Please refresh.")
            overview = {
                "total_farmers": 0,
                "active_farmers": 0,
                "deactivated_farmers": 0,
                "total_crops": 0,
                "active_crops": 0,
                "total_cultivated_acres": 0.0,
                "total_activities": 0,
                "total_expenses_count": 0,
                "total_expense_amount": 0.0,
                "total_harvest_count": 0,
                "total_harvest_revenue": 0.0,
                "total_harvest_quantity": 0.0,
                "total_conversations": 0,
                "total_messages": 0,
                "farmer_questions_asked": 0,
                "language_distribution": {},
                "top_districts": {},
            }

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric(
                label="👥 Registered Farmers",
                value=overview["total_farmers"],
                delta=f"{overview['active_farmers']} Active",
            )
        with kpi2:
            st.metric(
                label="🌾 Cultivated Crops",
                value=overview["total_crops"],
                delta=f"{overview['total_cultivated_acres']} Acres",
            )
        with kpi3:
            st.metric(
                label="🚜 Farm Activities",
                value=overview["total_activities"],
                delta=f"{overview['total_harvest_count']} Harvests",
            )
        with kpi4:
            st.metric(
                label="🤖 AI Farmer Queries",
                value=overview["farmer_questions_asked"],
                delta=f"{overview['total_conversations']} Sessions",
            )

        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

        kpi5, kpi6, kpi7, kpi8 = st.columns(4)
        with kpi5:
            st.metric(
                label="💸 Logged Expenses",
                value=format_inr(overview["total_expense_amount"]),
                delta=f"{overview['total_expenses_count']} Records",
            )
        with kpi6:
            st.metric(
                label="💰 Harvest Revenue",
                value=format_inr(overview["total_harvest_revenue"]),
                delta=f"{overview['total_harvest_quantity']} Output",
            )
        with kpi7:
            net_agri = overview["total_harvest_revenue"] - overview["total_expense_amount"]
            st.metric(
                label="⚖️ Net Farm Balance",
                value=format_inr(net_agri),
                delta="Profitable" if net_agri >= 0 else "-Deficit",
            )
        with kpi8:
            active_pct = round((overview["active_farmers"] / overview["total_farmers"] * 100), 1) if overview["total_farmers"] > 0 else 100.0
            st.metric(
                label="📈 Active User Rate",
                value=f"{active_pct}%",
                delta=f"{overview['deactivated_farmers']} Inactive",
            )

        st.markdown("---")
        c_lang, c_dist = st.columns([1, 1])
        with c_lang:
            st.markdown("##### 🌐 Language Preference Distribution")
            langs = overview.get("language_distribution", {})
            if langs:
                lang_display = {
                    "Marathi (मराठी)": langs.get("mr", 0),
                    "Hindi (हिंदी)": langs.get("hi", 0),
                    "English": langs.get("en", 0),
                }
                import pandas as pd
                df_lang = pd.DataFrame(list(lang_display.items()), columns=["Language", "Farmers"])
                st.dataframe(df_lang, use_container_width=True, hide_index=True)
            else:
                st.info("No language preference data recorded yet.")

        with c_dist:
            st.markdown("##### 📍 Top Districts by Farmer Count")
            top_d = overview.get("top_districts", {})
            if top_d:
                import pandas as pd
                df_dist = pd.DataFrame(list(top_d.items()), columns=["District", "Farmers"])
                st.dataframe(df_dist, use_container_width=True, hide_index=True)
            else:
                st.info("No district data recorded yet.")

    # =========================================================================
    # TAB 2: FARMER MANAGEMENT
    # =========================================================================
    elif admin_section == "👥 Farmers":
        st.subheader("👥 Farmer Account Management")
        st.caption("Search, filter, inspect profiles, and manage active status. Passwords and hashes are strictly concealed.")

        # Search & Filter Bar
        f_c1, f_c2, f_c3 = st.columns([2, 1, 1])
        with f_c1:
            search_query = st.text_input("🔍 Search Farmers", placeholder="Search by name, phone, email, or village...")
        with f_c2:
            status_filter_choice = st.selectbox("Status Filter", options=["All", "Active Only", "Deactivated Only"])
            is_active_arg = None
            if status_filter_choice == "Active Only":
                is_active_arg = True
            elif status_filter_choice == "Deactivated Only":
                is_active_arg = False
        with f_c3:
            dist_filter = st.text_input("District Filter", placeholder="e.g. Pune, Wardha, Amravati...")

        try:
            with get_db() as db:
                farmers_list, total_matched = AdminService.list_farmers(
                    db=db,
                    admin=admin,
                    search=search_query,
                    district=dist_filter if dist_filter else None,
                    is_active=is_active_arg,
                    limit=100,
                )
        except Exception as e:
            logger.exception("Failed to query farmers list: %s", e)
            st.warning("⚠️ Farmer accounts could not be retrieved at this moment.")
            farmers_list, total_matched = [], 0

        st.markdown(f"**Found {total_matched} registered farmers matching filters**")

        if farmers_list:
            import pandas as pd
            display_data = []
            for f in farmers_list:
                display_data.append({
                    "Farmer Name": f["full_name"],
                    "Phone": f["phone"],
                    "Village": f["village"],
                    "District": f["district"],
                    "State": f["state"],
                    "Landholding": f"{f['farm_size']} {f['farm_area_unit']}",
                    "Language": f["preferred_language"].upper(),
                    "Total Crops": f["total_crops"],
                    "Status": "🟢 Active" if f["is_active"] else "🔴 Inactive",
                    "Registered": f["created_at"],
                })

            df_farmers = pd.DataFrame(display_data)
            st.dataframe(df_farmers, use_container_width=True, hide_index=True)

            # Account Action Control
            st.markdown("---")
            st.markdown("##### ⚡ Manage Farmer Status")
            f_act_c1, f_act_c2 = st.columns([3, 1])
            with f_act_c1:
                selected_farmer_opt = st.selectbox(
                    "Select Farmer to Toggle Status",
                    options=farmers_list,
                    format_func=lambda x: f"{x['full_name']} ({x['phone']} • {x['district']}) — {'Active' if x['is_active'] else 'Deactivated'}",
                    key="sel_farmer_toggle",
                )
            with f_act_c2:
                if selected_farmer_opt:
                    current_status = selected_farmer_opt["is_active"]
                    toggle_btn_label = "🔴 Deactivate Account" if current_status else "🟢 Activate Account"
                    btn_color = "secondary" if current_status else "primary"
                    if st.button(toggle_btn_label, key="btn_toggle_farmer", use_container_width=True, type=btn_color):
                        with get_db() as db:
                            new_st = not current_status
                            AdminService.toggle_farmer_status(db, admin, selected_farmer_opt["id"], new_st)
                        st.success(f"Updated status for {selected_farmer_opt['full_name']} to {'Active' if new_st else 'Deactivated'}!")
                        st.rerun()
        else:
            st.info("No farmers found matching the search criteria.")

    # =========================================================================
    # TAB 3: CROP ANALYTICS
    # =========================================================================
    elif admin_section == "🌾 Crop Analytics":
        st.subheader("🌾 Crop Cultivation & Distribution Analytics")
        try:
            with get_db() as db:
                crop_analytics = AdminService.get_crop_analytics(db, admin)
        except Exception as e:
            logger.exception("Failed to load crop analytics: %s", e)
            st.warning("⚠️ Crop analytics are temporarily unavailable.")
            crop_analytics = {
                "popular_crops": [],
                "growth_stages": {},
                "status_distribution": {},
                "district_crops": [],
                "average_plot_size": 0.0,
            }

        ca_col1, ca_col2 = st.columns([3, 2])
        with ca_col1:
            st.markdown("##### 🏆 Popular Crops (By Frequency & Total Acreage)")
            pop_crops = crop_analytics.get("popular_crops", [])
            if pop_crops:
                import pandas as pd
                df_pop = pd.DataFrame(pop_crops)
                df_pop.columns = ["Crop Name", "Registered Plots", "Total Acreage (Acres)"]
                st.dataframe(df_pop, use_container_width=True, hide_index=True)
            else:
                st.info("No crop cultivation data recorded yet.")

        with ca_col2:
            st.markdown("##### 🌱 Growth Stages Distribution")
            stages = crop_analytics.get("growth_stages", {})
            if stages:
                import pandas as pd
                df_stages = pd.DataFrame(list(stages.items()), columns=["Growth Stage", "Plots"])
                st.dataframe(df_stages, use_container_width=True, hide_index=True)
            else:
                st.info("No growth stage data available.")

        st.markdown("---")
        st.markdown("##### 📍 Geographic Crop Distribution by District")
        dist_crops = crop_analytics.get("district_crops", [])
        if dist_crops:
            import pandas as pd
            df_dc = pd.DataFrame(dist_crops)
            df_dc.columns = ["District", "Dominant Crop", "Plot Count"]
            st.dataframe(df_dc, use_container_width=True, hide_index=True)
        else:
            st.info("No district-level crop data recorded yet.")

    # =========================================================================
    # TAB 4: ACTIVITY ANALYTICS
    # =========================================================================
    elif admin_section == "🚜 Activities":
        st.subheader("🚜 Agricultural Operations & Field Activities")
        try:
            with get_db() as db:
                act_analytics = AdminService.get_activity_analytics(db, admin)
        except Exception as e:
            logger.exception("Failed to load activity analytics: %s", e)
            st.warning("⚠️ Activity analytics are temporarily unavailable.")
            act_analytics = {
                "activity_types": [],
                "crops_with_activities": {},
                "total_activities": 0,
                "total_activity_cost": 0.0,
            }

        st.metric(
            label="Total Logged Field Operations",
            value=act_analytics.get("total_activities", 0),
            delta=f"Total Operations Cost: {format_inr(act_analytics.get('total_activity_cost', 0.0))}",
        )

        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
        act_c1, act_c2 = st.columns([3, 2])
        with act_c1:
            st.markdown("##### 📋 Breakdown by Activity Type")
            act_types = act_analytics.get("activity_types", [])
            if act_types:
                import pandas as pd
                df_act = pd.DataFrame(act_types)
                df_act.columns = ["Activity Type", "Logged Frequency", "Total Cost (₹)"]
                df_act["Total Cost (₹)"] = df_act["Total Cost (₹)"].apply(lambda x: format_inr(x))
                st.dataframe(df_act, use_container_width=True, hide_index=True)
            else:
                st.info("No field activities recorded yet.")

        with act_c2:
            st.markdown("##### 🌾 Crops Receiving Most Operations")
            top_crops_acts = act_analytics.get("crops_with_activities", {})
            if top_crops_acts:
                import pandas as pd
                df_tc = pd.DataFrame(list(top_crops_acts.items()), columns=["Crop", "Total Activities"])
                st.dataframe(df_tc, use_container_width=True, hide_index=True)
            else:
                st.info("No operations mapped to crops yet.")

    # =========================================================================
    # TAB 5: FINANCIAL HEALTH ANALYTICS
    # =========================================================================
    elif admin_section == "💰 Financial Health":
        st.subheader("💰 Platform Financial & Cultivation Economics")
        try:
            with get_db() as db:
                fin_analytics = AdminService.get_financial_analytics(db, admin)
        except Exception as e:
            logger.exception("Failed to load financial analytics: %s", e)
            st.warning("⚠️ Financial analytics are temporarily unavailable.")
            fin_analytics = {
                "categories": [],
                "revenue_by_crop": [],
                "total_expense": 0.0,
                "total_revenue": 0.0,
                "net_profit": 0.0,
                "avg_cost_per_acre": 0.0,
            }

        f_kpi1, f_kpi2, f_kpi3, f_kpi4 = st.columns(4)
        with f_kpi1:
            st.metric("Total Platform Expenses", format_inr(fin_analytics.get("total_expense", 0.0)))
        with f_kpi2:
            st.metric("Total Harvest Revenue", format_inr(fin_analytics.get("total_revenue", 0.0)))
        with f_kpi3:
            net_val = fin_analytics.get("net_profit", 0.0)
            st.metric("Net Agricultural Profit", format_inr(net_val), delta="Profitable" if net_val >= 0 else "-Deficit")
        with f_kpi4:
            st.metric("Average Cost per Acre", format_inr(fin_analytics.get("avg_cost_per_acre", 0.0)))

        st.markdown("---")
        fin_c1, fin_c2 = st.columns([1, 1])
        with fin_c1:
            st.markdown("##### 💸 Input Expenses by Category")
            cats = fin_analytics.get("categories", [])
            if cats:
                import pandas as pd
                df_cat = pd.DataFrame(cats)
                df_cat.columns = ["Category", "Transaction Count", "Total Amount (₹)"]
                df_cat["Total Amount (₹)"] = df_cat["Total Amount (₹)"].apply(lambda x: format_inr(x))
                st.dataframe(df_cat, use_container_width=True, hide_index=True)
            else:
                st.info("No farm expenses recorded yet.")

        with fin_c2:
            st.markdown("##### 🌾 Revenue Generated by Crop")
            rev_crops = fin_analytics.get("revenue_by_crop", [])
            if rev_crops:
                import pandas as pd
                df_rc = pd.DataFrame(rev_crops)
                df_rc.columns = ["Crop", "Total Sales Revenue (₹)", "Total Quantity Produced"]
                df_rc["Total Sales Revenue (₹)"] = df_rc["Total Sales Revenue (₹)"].apply(lambda x: format_inr(x))
                st.dataframe(df_rc, use_container_width=True, hide_index=True)
            else:
                st.info("No harvest revenue recorded yet.")

    # =========================================================================
    # TAB 6: AI USAGE & TOPICS ANALYTICS
    # =========================================================================
    elif admin_section == "🤖 AI Usage":
        st.subheader("🤖 AI Advisor Usage & Topic Intelligence")
        st.caption("Privacy Notice: Individual conversations remain confidential. Aggregated topic frequencies and system volumes are shown.")

        try:
            with get_db() as db:
                ai_analytics = AdminService.get_ai_usage_analytics(db, admin)
        except Exception as e:
            logger.exception("Failed to load AI usage analytics: %s", e)
            st.warning("⚠️ AI usage analytics are temporarily unavailable.")
            ai_analytics = {
                "total_conversations": 0,
                "total_questions": 0,
                "language_distribution": {},
                "popular_topics": [],
            }

        ai_k1, ai_k2 = st.columns(2)
        with ai_k1:
            st.metric("Total AI Consultations", ai_analytics.get("total_questions", 0))
        with ai_k2:
            st.metric("Total Chat Sessions", ai_analytics.get("total_conversations", 0))

        st.markdown("---")
        st.markdown("##### 🔍 Most Frequently Asked Agricultural Topics")
        pop_topics = ai_analytics.get("popular_topics", [])
        if pop_topics:
            import pandas as pd
            df_topics = pd.DataFrame(pop_topics)
            df_topics.columns = ["Farming Domain / Problem Area", "Query Frequency"]
            st.dataframe(df_topics, use_container_width=True, hide_index=True)
        else:
            st.info("No AI consultations recorded yet.")

    # =========================================================================
    # TAB 7: DATA EXPORTS (CSV, EXCEL XLSX, JSON)
    # =========================================================================
    elif admin_section == "📥 Data Exports":
        st.subheader("📥 Authorized & Sanitized Data Exports")
        st.markdown(
            textwrap.dedent("""
            <div style="background: #e8f5e9; border: 1.5px solid #a5d6a7; border-radius: 10px; padding: 12px 16px; margin-bottom: 18px; font-size: 0.92rem; color: #1b5e20;">
                🔒 <strong>Security & Privacy Guarantee:</strong> All exports strictly omit password hashes, tokens, API keys, and private chats.
                Exports are generated in UTF-8 BOM encoding for seamless Microsoft Excel compatibility with Devanagari (Marathi/Hindi).
                Every export is permanently recorded in the Admin Audit Log.
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

        exp_c1, exp_c2, exp_c3 = st.columns([2, 1, 1])
        with exp_c1:
            export_module = st.selectbox(
                "Select Data Module",
                options=["farmers", "crops", "expenses", "harvest", "activities", "overview"],
                format_func=lambda x: {
                    "farmers": "👥 Registered Farmers (Sanitized)",
                    "crops": "🌾 Crops & Growth Stages",
                    "expenses": "💸 Farm Expenses & Categories",
                    "harvest": "💰 Harvest Records & Revenue",
                    "activities": "🚜 Field Activities & Operations",
                    "overview": "📊 Platform Summary Snapshot",
                }.get(x, x),
            )
        with exp_c2:
            export_fmt = st.selectbox(
                "Export Format",
                options=["csv", "xlsx", "json"],
                format_func=lambda x: {
                    "csv": "CSV (UTF-8 BOM for Excel)",
                    "xlsx": "Excel Workbook (.xlsx)",
                    "json": "JSON (.json)",
                }.get(x, x),
            )
        with exp_c3:
            exp_district_filter = st.text_input("District Filter (Optional)", placeholder="All / Pune / Wardha...")

        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

        if st.button("🚀 Generate & Download Export", key="btn_run_export", type="primary", use_container_width=True):
            try:
                with get_db() as db:
                    filters_applied = {}
                    if exp_district_filter and exp_district_filter.strip():
                        filters_applied["district"] = exp_district_filter.strip()

                    data_bytes, filename, mime_type = AdminService.export_data(
                        db=db,
                        admin=admin,
                        module=export_module,
                        export_format=export_fmt,
                        filters=filters_applied,
                    )

                st.success(f"✅ Generated {filename} ({len(data_bytes):,} bytes)!")
                st.download_button(
                    label=f"⬇️ Click to Download {filename}",
                    data=data_bytes,
                    file_name=filename,
                    mime=mime_type,
                    key="btn_download_exported_data",
                    use_container_width=True,
                )
            except Exception as exp_err:
                st.error(f"❌ Export failed: {exp_err}")

    # =========================================================================
    # TAB 8: BACKUP, PERSISTENCE & POSTGRESQL MIGRATION
    # =========================================================================
    elif admin_section == "🛡️ Backup & Maintenance":
        st.subheader("🛡️ Database Persistence, Backups & Migration Architecture")

        # 1. Active Database Engine Diagnostic Card
        db_info = get_database_info()
        is_persistent = db_info.get("is_persistent", False)

        if is_persistent:
            st.success(
                f"✅ **Persistent Cloud Database Active:** Connected to `{db_info.get('engine')}` (`{db_info.get('sanitized_url')}`). "
                "Farmer records and agricultural data are stored permanently on durable cloud storage and will persist across all Streamlit Cloud reboots, sleeps, and redeployments."
            )
        else:
            st.warning(
                "⚠️ **Development SQLite Database Active:** Currently running on local disk storage (`data/agrisaathi.db`). "
                "For Streamlit Community Cloud production deployments, configure `DATABASE_URL` in Streamlit Secrets pointing to a persistent PostgreSQL database (e.g. Neon or Supabase) to ensure farmer records persist permanently."
            )

        with st.expander("🔍 Connection Pooling & Storage Diagnostics", expanded=False):
            diag_c1, diag_c2, diag_c3 = st.columns(3)
            with diag_c1:
                st.metric("Database Engine", db_info.get("engine", "unknown").upper())
                st.metric("SQLAlchemy Dialect", db_info.get("dialect", "unknown"))
            with diag_c2:
                st.metric("Storage Durability", "Cloud Persistent" if is_persistent else "Local Ephemeral")
                st.metric("Connection Pre-Ping", "Active (pool_pre_ping=True)")
            with diag_c3:
                st.metric("Connection Pool Size", str(db_info.get("pool_size", "N/A")))
                st.metric("Pool Recycle (Seconds)", str(db_info.get("pool_recycle_seconds", "N/A")))

        st.markdown("---")
        st.markdown("##### 1. One-Click Database Snapshot & Backup")
        st.caption("Creates an immediate, atomic snapshot of all tables, foreign keys, and farmer records.")

        bak_col1, bak_col2 = st.columns([2, 1])
        with bak_col1:
            btn_label = "💾 Create SQLite Database Backup Now" if not is_persistent else "💾 Create Portable JSON Snapshot Now"
            if st.button(btn_label, key="btn_create_backup", type="primary", use_container_width=True):
                try:
                    dest_p, b_name, b_sz = BackupService.create_backup(admin)
                    st.success(f"✅ Backup created successfully: **{b_name}** ({round(b_sz / 1024, 1)} KB)")
                    st.rerun()
                except Exception as bak_err:
                    st.error(f"❌ Backup creation failed: {bak_err}")

        # List Existing Backups
        existing_backups = BackupService.list_backups(admin)
        if existing_backups:
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            st.markdown(f"**Available Backups ({len(existing_backups)}):**")
            for b in existing_backups[:8]:
                b_c1, b_c2 = st.columns([3, 1])
                with b_c1:
                    fmt_label = b.get("format", "Backup")
                    st.markdown(f"📦 **{b['filename']}** ({fmt_label} • {b['size_mb']} MB • {b['created_at']})")
                with b_c2:
                    try:
                        with open(b["path"], "rb") as bf:
                            bytes_data = bf.read()
                        mime_t = "application/json" if b["filename"].endswith(".json") else "application/x-sqlite3"
                        st.download_button(
                            label="⬇️ Download",
                            data=bytes_data,
                            file_name=b["filename"],
                            mime=mime_t,
                            key=f"dl_backup_{b['filename']}",
                            use_container_width=True,
                        )
                    except Exception:
                        st.caption("Download error")

        st.markdown("---")
        st.markdown("##### 2. Restore Database from Backup File")
        st.caption("Safety Notice: A pre-restore safety snapshot of the active database is automatically created before any restoration.")

        restore_file = st.file_uploader(
            "Upload Valid Backup File (.db or .json)",
            type=["db", "sqlite", "sqlite3", "json"],
            key="restore_db_uploader",
        )

        confirm_restore = st.checkbox("⚠️ I understand that restoring will update or overwrite active database records.", key="chk_confirm_restore")

        if restore_file and confirm_restore:
            if st.button("🚨 Execute Database Restore", key="btn_run_restore", type="secondary"):
                try:
                    bytes_to_restore = restore_file.read()
                    res = BackupService.restore_backup(admin, bytes_to_restore)
                    st.success(f"✅ {res['message']} (Restored {round(res['restored_size_bytes'] / 1024, 1)} KB)")
                    if res.get("safety_snapshot"):
                        st.info(f"Pre-restore safety backup preserved at: `{res.get('safety_snapshot')}`")
                except Exception as rest_err:
                    st.error(f"❌ Restore failed: {rest_err}")

        st.markdown("---")
        st.markdown("##### 3. Production PostgreSQL Setup & Migration Guide")
        st.markdown(
            textwrap.dedent("""
            To achieve **permanent, durable farmer record retention** that survives Streamlit Cloud reboots, inactivity sleep, and redeployments:

            **Step A: Provision a Free Managed PostgreSQL Database**
            1. Create a free account at [Neon.tech](https://neon.tech) (recommended, zero-idle sleep wake-ups) or [Supabase.com](https://supabase.com).
            2. Copy your connection URI string:
               `postgresql://[user]:[password]@[endpoint].neon.tech/neondb?sslmode=require`

            **Step B: Migrate Existing SQLite Records to PostgreSQL**
            ```bash
            # 1. Dry run inspection (verifies tables and row parity)
            python scripts/migrate_sqlite_to_postgres.py --dry-run

            # 2. Live migration to your target PostgreSQL database
            python scripts/migrate_sqlite_to_postgres.py --sqlite-path ./data/agrisaathi.db --postgres-url "postgresql://[user]:[password]@[endpoint].neon.tech/neondb?sslmode=require"
            ```

            **Step C: Configure Streamlit Community Cloud Secrets**
            In your Streamlit Cloud Dashboard, open **App Settings > Secrets** and paste:
            ```toml
            DATABASE_URL = "postgresql://[user]:[password]@[endpoint].neon.tech/neondb?sslmode=require"
            ADMIN_EMAIL = "admin@agrisaathi.internal"
            ADMIN_PASSWORD = "YourSecurePassword123!"
            ```
            The application will automatically connect to the durable PostgreSQL instance on startup and retain all farmer records forever.
            """).strip()
        )

    # =========================================================================
    # TAB 9: AUDIT LOGS
    # =========================================================================
    elif admin_section == "📜 Audit Logs":
        st.subheader("📜 Administrative Activity & Audit Trail")
        st.caption("Chronological record of admin actions, record access, status changes, and data exports.")

        audit_filter_col1, audit_filter_col2 = st.columns([2, 1])
        with audit_filter_col1:
            audit_action_filter = st.selectbox(
                "Filter by Action Type",
                options=["all", "LOGIN", "EXPORT_DATA", "TOGGLE_STATUS", "BACKUP_DB", "RESTORE_DB", "VIEW_FARMERS"],
                format_func=lambda x: "All Actions" if x == "all" else x,
                key="audit_action_filter_select",
            )
        with audit_filter_col2:
            audit_limit = st.selectbox("Log Limit", options=[25, 50, 100, 200], index=1)

        with get_db() as db:
            logs = AdminService.get_audit_logs(
                db=db,
                admin=admin,
                limit=audit_limit,
                action_filter=audit_action_filter,
            )

        if logs:
            import pandas as pd
            display_logs = []
            for l_item in logs:
                details_text = ""
                if l_item["details"]:
                    if isinstance(l_item["details"], dict):
                        details_text = ", ".join(f"{k}: {v}" for k, v in l_item["details"].items())
                    else:
                        details_text = str(l_item["details"])

                display_logs.append({
                    "Timestamp (UTC)": l_item["created_at"],
                    "Administrator": l_item["admin_name"],
                    "Action": l_item["action"],
                    "Resource": f"{l_item['resource_type']}{' (' + str(l_item['resource_id']) + ')' if l_item['resource_id'] else ''}",
                    "Details": details_text[:80] + ("..." if len(details_text) > 80 else ""),
                })

            df_logs = pd.DataFrame(display_logs)
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.info("No administrative activity logged yet.")
