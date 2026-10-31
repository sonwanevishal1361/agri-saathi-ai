"""Developer Admin Panel Service and Analytics Engine for AgriSaathi AI.

Provides role-based system monitoring, farmer management, agricultural analytics,
audit logging, and sanitized data exports (CSV, Excel XLSX, JSON).
Strictly enforces administrator privileges (require_admin) on all operations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timezone
import json
import io
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from core.auth import AuthenticatedFarmer, require_admin
from models.user import User
from models.crop import Crop
from models.activity import FarmActivity
from models.expense import Expense
from models.harvest import HarvestRecord
from models.conversation import Conversation, Message
from models.admin_log import AdminAuditLog
from utils.logging_config import logger


class AdminService:
    """Central administrative service for platform developer and application owner."""

    @classmethod
    def log_action(
        cls,
        db: Session,
        admin: AuthenticatedFarmer,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AdminAuditLog:
        """Record an administrative action to the persistent audit log."""
        require_admin(admin)
        details_str = json.dumps(details, default=str) if details else None

        # Ensure admin_id matches a persistent User record to respect foreign keys
        actual_admin_id = None
        if admin and admin.id:
            exists = db.query(User.id).filter(User.id == admin.id).first()
            if exists:
                actual_admin_id = admin.id

        log_entry = AdminAuditLog(
            admin_id=actual_admin_id,
            admin_name=admin.full_name if admin else "System Administrator",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details_str,
            ip_address=ip_address,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        logger.info(f"Admin action logged: {action} on {resource_type} by {admin.full_name} ({admin.id})")
        return log_entry

    @classmethod
    def get_audit_logs(
        cls,
        db: Session,
        admin: AuthenticatedFarmer,
        limit: int = 100,
        action_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent administrative audit logs."""
        require_admin(admin)
        query = db.query(AdminAuditLog)
        if action_filter and action_filter.lower() != "all":
            query = query.filter(AdminAuditLog.action == action_filter.strip())

        logs = query.order_by(desc(AdminAuditLog.created_at)).limit(limit).all()
        result = []
        for log_item in logs:
            parsed_details = None
            if log_item.details:
                try:
                    parsed_details = json.loads(log_item.details)
                except Exception:
                    parsed_details = log_item.details

            result.append({
                "id": log_item.id,
                "admin_name": log_item.admin_name,
                "action": log_item.action,
                "resource_type": log_item.resource_type,
                "resource_id": log_item.resource_id,
                "details": parsed_details,
                "ip_address": log_item.ip_address,
                "created_at": log_item.created_at.strftime("%Y-%m-%d %H:%M:%S") if log_item.created_at else "",
            })
        return result

    @classmethod
    def get_system_overview(cls, db: Session, admin: AuthenticatedFarmer) -> Dict[str, Any]:
        """Aggregate platform overview metrics for developers and application owners."""
        require_admin(admin)

        # Farmers count (excluding admin accounts)
        total_farmers = db.query(func.count(User.id)).filter(User.role != "admin").scalar() or 0
        active_farmers = db.query(func.count(User.id)).filter(User.role != "admin", User.is_active.is_(True)).scalar() or 0

        # Crops metrics
        total_crops = db.query(func.count(Crop.id)).scalar() or 0
        active_crops = db.query(func.count(Crop.id)).filter(Crop.status == "active").scalar() or 0
        total_acres = db.query(func.sum(Crop.area)).scalar() or 0.0

        # Activities metrics
        total_activities = db.query(func.count(FarmActivity.id)).scalar() or 0

        # Expenses metrics
        total_expenses_count = db.query(func.count(Expense.id)).scalar() or 0
        total_expense_amount = db.query(func.sum(Expense.amount)).scalar() or 0.0

        # Harvest metrics
        harvest_records = db.query(HarvestRecord).all()
        total_harvest_count = len(harvest_records)
        total_harvest_revenue = sum(h.total_revenue for h in harvest_records)
        total_harvest_qty = sum(float(h.quantity or 0.0) for h in harvest_records)

        # AI Usage metrics
        total_conversations = db.query(func.count(Conversation.id)).scalar() or 0
        total_messages = db.query(func.count(Message.id)).scalar() or 0
        farmer_questions = db.query(func.count(Message.id)).filter(Message.role == "user").scalar() or 0

        # Language distribution
        lang_rows = (
            db.query(User.preferred_language, func.count(User.id))
            .filter(User.role != "admin")
            .group_by(User.preferred_language)
            .all()
        )
        lang_distribution = {row[0] or "en": row[1] for row in lang_rows}

        # Districts distribution
        dist_rows = (
            db.query(User.district, func.count(User.id))
            .filter(User.role != "admin", User.district.isnot(None))
            .group_by(User.district)
            .order_by(desc(func.count(User.id)))
            .limit(10)
            .all()
        )
        top_districts = {row[0]: row[1] for row in dist_rows if row[0]}

        return {
            "total_farmers": total_farmers,
            "active_farmers": active_farmers,
            "deactivated_farmers": total_farmers - active_farmers,
            "total_crops": total_crops,
            "active_crops": active_crops,
            "total_cultivated_acres": round(float(total_acres), 2),
            "total_activities": total_activities,
            "total_expenses_count": total_expenses_count,
            "total_expense_amount": round(float(total_expense_amount), 2),
            "total_harvest_count": total_harvest_count,
            "total_harvest_revenue": round(float(total_harvest_revenue), 2),
            "total_harvest_quantity": round(float(total_harvest_qty), 2),
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "farmer_questions_asked": farmer_questions,
            "language_distribution": lang_distribution,
            "top_districts": top_districts,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    @classmethod
    def list_farmers(
        cls,
        db: Session,
        admin: AuthenticatedFarmer,
        search: Optional[str] = None,
        district: Optional[str] = None,
        village: Optional[str] = None,
        state: Optional[str] = None,
        is_active: Optional[bool] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch filtered farmer records with sanitized fields (strictly NO password hashes)."""
        require_admin(admin)

        query = db.query(User).filter(User.role != "admin")

        if search and search.strip():
            s = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(User.full_name).like(s),
                    func.lower(User.phone).like(s),
                    func.lower(User.email).like(s),
                    func.lower(User.village).like(s),
                    func.lower(User.district).like(s),
                )
            )

        if district and district.lower() != "all":
            query = query.filter(func.lower(User.district) == district.strip().lower())

        if village and village.strip() and village.lower() != "all":
            query = query.filter(func.lower(User.village).like(f"%{village.strip().lower()}%"))

        if state and state.lower() != "all":
            query = query.filter(func.lower(User.state) == state.strip().lower())

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if date_from:
            query = query.filter(User.created_at >= datetime.combine(date_from, datetime.min.time()))

        if date_to:
            query = query.filter(User.created_at <= datetime.combine(date_to, datetime.max.time()))

        total_count = query.count()
        farmers = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()

        results = []
        for f in farmers:
            crop_count = len(f.crops) if f.crops else 0
            results.append({
                "id": f.id,
                "full_name": f.full_name,
                "phone": f.phone or "—",
                "email": f.email or "—",
                "village": f.village or "—",
                "district": f.district or "—",
                "state": f.state or "—",
                "farm_size": f.farm_size or 0.0,
                "farm_area_unit": f.farm_area_unit or "Acre",
                "soil_type": f.soil_type or "—",
                "irrigation_method": f.irrigation_method or "—",
                "preferred_language": f.preferred_language or "en",
                "is_active": f.is_active,
                "role": f.role,
                "total_crops": crop_count,
                "created_at": f.created_at.strftime("%Y-%m-%d %H:%M") if f.created_at else "—",
            })

        return results, total_count

    @classmethod
    def toggle_farmer_status(
        cls,
        db: Session,
        admin: AuthenticatedFarmer,
        farmer_id: str,
        new_status: bool,
    ) -> User:
        """Activate or deactivate a farmer account with audit logging."""
        require_admin(admin)
        farmer = db.query(User).filter(User.id == farmer_id).first()
        if not farmer:
            raise ValueError(f"Farmer with ID {farmer_id} not found.")

        old_status = farmer.is_active
        farmer.is_active = new_status
        db.commit()
        db.refresh(farmer)

        cls.log_action(
            db=db,
            admin=admin,
            action="TOGGLE_STATUS",
            resource_type="farmer",
            resource_id=farmer_id,
            details={
                "farmer_name": farmer.full_name,
                "old_status": old_status,
                "new_status": new_status,
            },
        )
        return farmer

    @classmethod
    def get_crop_analytics(cls, db: Session, admin: AuthenticatedFarmer) -> Dict[str, Any]:
        """Aggregate crop popularity, geographic distribution, and growth stage analytics."""
        require_admin(admin)

        # Popular crops by frequency and total acreage
        pop_rows = (
            db.query(
                Crop.name,
                func.count(Crop.id).label("count"),
                func.sum(Crop.area).label("total_area"),
            )
            .group_by(Crop.name)
            .order_by(desc("count"))
            .all()
        )
        popular_crops = [
            {
                "crop": row[0],
                "count": row[1],
                "total_area": round(float(row[2] or 0.0), 2),
            }
            for row in pop_rows
        ]

        # Growth stage distribution
        stage_rows = (
            db.query(Crop.growth_stage, func.count(Crop.id))
            .group_by(Crop.growth_stage)
            .order_by(desc(func.count(Crop.id)))
            .all()
        )
        stages = {row[0] or "Unknown": row[1] for row in stage_rows}

        # Status distribution (active, harvested, failed)
        status_rows = (
            db.query(Crop.status, func.count(Crop.id))
            .group_by(Crop.status)
            .all()
        )
        statuses = {row[0] or "active": row[1] for row in status_rows}

        # District-wise crop cultivation
        dist_crop_rows = (
            db.query(User.district, Crop.name, func.count(Crop.id))
            .join(Crop, User.id == Crop.farmer_id)
            .filter(User.district.isnot(None))
            .group_by(User.district, Crop.name)
            .order_by(desc(func.count(Crop.id)))
            .limit(20)
            .all()
        )
        district_crops = [
            {"district": r[0], "crop": r[1], "count": r[2]}
            for r in dist_crop_rows if r[0] and r[1]
        ]

        avg_plot_size = db.query(func.avg(Crop.area)).scalar() or 0.0

        return {
            "popular_crops": popular_crops,
            "growth_stages": stages,
            "status_distribution": statuses,
            "district_crops": district_crops,
            "average_plot_size": round(float(avg_plot_size), 2),
        }

    @classmethod
    def get_activity_analytics(cls, db: Session, admin: AuthenticatedFarmer) -> Dict[str, Any]:
        """Aggregate farm activities breakdown, top operations, and costs."""
        require_admin(admin)

        # Breakdown by activity type
        type_rows = (
            db.query(
                FarmActivity.activity_type,
                func.count(FarmActivity.id).label("count"),
                func.sum(FarmActivity.cost).label("total_cost"),
            )
            .group_by(FarmActivity.activity_type)
            .order_by(desc("count"))
            .all()
        )
        activity_types = [
            {
                "activity_type": r[0] or "General",
                "count": r[1],
                "total_cost": round(float(r[2] or 0.0), 2),
            }
            for r in type_rows
        ]

        # Top crops receiving farm activities
        top_crop_acts = (
            db.query(Crop.name, func.count(FarmActivity.id))
            .join(FarmActivity, Crop.id == FarmActivity.crop_id)
            .group_by(Crop.name)
            .order_by(desc(func.count(FarmActivity.id)))
            .limit(10)
            .all()
        )
        crops_with_activities = {r[0]: r[1] for r in top_crop_acts}

        return {
            "activity_types": activity_types,
            "crops_with_activities": crops_with_activities,
            "total_activities": sum(item["count"] for item in activity_types),
            "total_activity_cost": sum(item["total_cost"] for item in activity_types),
        }

    @classmethod
    def get_financial_analytics(cls, db: Session, admin: AuthenticatedFarmer) -> Dict[str, Any]:
        """Aggregate financial health, category expenses, harvest revenue, and net profit."""
        require_admin(admin)

        # Expense by category
        cat_rows = (
            db.query(
                Expense.category,
                func.count(Expense.id).label("count"),
                func.sum(Expense.amount).label("total"),
            )
            .group_by(Expense.category)
            .order_by(desc("total"))
            .all()
        )
        categories = [
            {
                "category": r[0] or "Other",
                "count": r[1],
                "total_amount": round(float(r[2] or 0.0), 2),
            }
            for r in cat_rows
        ]

        total_expense = sum(c["total_amount"] for c in categories)

        # Harvest revenue by crop
        crop_rev_map: Dict[str, Dict[str, float]] = {}
        for h in db.query(HarvestRecord).all():
            c_name = h.crop.name if h.crop else "General"
            if c_name not in crop_rev_map:
                crop_rev_map[c_name] = {"total_revenue": 0.0, "total_quantity": 0.0}
            crop_rev_map[c_name]["total_revenue"] += h.total_revenue
            crop_rev_map[c_name]["total_quantity"] += float(h.quantity or 0.0)

        revenue_by_crop = [
            {
                "crop": c_name,
                "total_revenue": round(data["total_revenue"], 2),
                "total_quantity": round(data["total_quantity"], 2),
            }
            for c_name, data in sorted(crop_rev_map.items(), key=lambda x: x[1]["total_revenue"], reverse=True)
        ]

        total_revenue = sum(item["total_revenue"] for item in revenue_by_crop)
        net_agricultural_profit = total_revenue - total_expense

        # Total acreage for cost per acre calculation
        total_acres = db.query(func.sum(Crop.area)).scalar() or 0.0
        avg_cost_per_acre = round(total_expense / total_acres, 2) if total_acres > 0 else 0.0

        return {
            "categories": categories,
            "revenue_by_crop": revenue_by_crop,
            "total_expense": round(total_expense, 2),
            "total_revenue": round(total_revenue, 2),
            "net_profit": round(net_agricultural_profit, 2),
            "avg_cost_per_acre": avg_cost_per_acre,
        }

    @classmethod
    def get_ai_usage_analytics(cls, db: Session, admin: AuthenticatedFarmer) -> Dict[str, Any]:
        """Aggregate AI chatbot usage, languages, and popular agricultural topics with privacy preservation."""
        require_admin(admin)

        total_conversations = db.query(func.count(Conversation.id)).scalar() or 0
        user_queries = db.query(Message).filter(Message.role == "user").all()
        total_questions = len(user_queries)

        # Language distribution based on conversations and user preferences
        lang_counts: Dict[str, int] = {"mr": 0, "hi": 0, "en": 0}
        for u in db.query(User).filter(User.role != "admin").all():
            pref = u.preferred_language or "en"
            lang_counts[pref] = lang_counts.get(pref, 0) + 1

        # Anonymized keyword frequency for agricultural topics
        keywords_map = {
            "बोंडअळी / Pink Bollworm": ["बोंडअळी", "bollworm", "sundi", "गुलाबी सुंडी", "कीड"],
            "खत व्यवस्थापन / Fertilizers": ["खत", "fertilizer", "खाद", "युरिया", "dap", "10:26:26"],
            "करपा / Blight Disease": ["करपा", "blight", "झुलसा", "मवा", "तुडतुडे"],
            "फवारणी / Spraying Advice": ["फवारणी", "spray", "छिड़काव", "औषध", "कीटकनाशक"],
            "पाणी व्यवस्थापन / Irrigation": ["पाणी", "water", "सिंचन", "ठिबक", "irrigation"],
            "हवामान / Weather Forecast": ["हवामान", "weather", "पाऊस", "rain", "तापमान"],
            "सरकारी योजना / Schemes": ["योजना", "अनुदान", "subsidy", "pm-kisan", "विमा"],
            "बाजारभाव / Mandi Prices": ["बाजारभाव", "भाव", "दर", "mandi", "apmc", "market"],
        }

        topic_counts = {topic: 0 for topic in keywords_map}
        for q in user_queries:
            text_low = (q.content or "").lower()
            for topic, words in keywords_map.items():
                if any(w.lower() in text_low for w in words):
                    topic_counts[topic] += 1

        sorted_topics = sorted(
            [{"topic": k, "count": v} for k, v in topic_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )

        return {
            "total_conversations": total_conversations,
            "total_questions": total_questions,
            "language_distribution": lang_counts,
            "popular_topics": sorted_topics,
        }

    @classmethod
    def export_data(
        cls,
        db: Session,
        admin: AuthenticatedFarmer,
        module: str,
        export_format: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bytes, str, str]:
        """Generate sanitized, authorized data export in CSV, Excel (XLSX), or JSON.

        Strictly strips password hashes, tokens, API keys, and internal secrets.
        Logs every export event to the Admin Audit Log.
        """
        require_admin(admin)
        f = filters or {}
        mod = module.strip().lower()
        fmt = export_format.strip().lower()

        records: List[Dict[str, Any]] = []

        if mod == "farmers":
            # Sanitize farmer records
            query = db.query(User).filter(User.role != "admin")
            if f.get("district") and f["district"].lower() != "all":
                query = query.filter(func.lower(User.district) == f["district"].strip().lower())
            if f.get("state") and f["state"].lower() != "all":
                query = query.filter(func.lower(User.state) == f["state"].strip().lower())
            if f.get("is_active") is not None:
                query = query.filter(User.is_active == f["is_active"])

            farmers = query.all()
            for u in farmers:
                records.append({
                    "farmer_id": u.id,
                    "full_name": u.full_name,
                    "phone": u.phone or "",
                    "email": u.email or "",
                    "village": u.village or "",
                    "district": u.district or "",
                    "state": u.state or "",
                    "farm_size": u.farm_size or 0.0,
                    "farm_area_unit": u.farm_area_unit or "Acre",
                    "soil_type": u.soil_type or "",
                    "irrigation_method": u.irrigation_method or "",
                    "preferred_language": u.preferred_language or "en",
                    "is_active": u.is_active,
                    "registered_date": u.created_at.strftime("%Y-%m-%d") if u.created_at else "",
                })

        elif mod == "crops":
            query = db.query(Crop).join(User, Crop.farmer_id == User.id)
            if f.get("district") and f["district"].lower() != "all":
                query = query.filter(func.lower(User.district) == f["district"].strip().lower())
            if f.get("crop") and f["crop"].lower() != "all":
                query = query.filter(func.lower(Crop.name).like(f"%{f['crop'].strip().lower()}%"))
            if f.get("status") and f["status"].lower() != "all":
                query = query.filter(Crop.status == f["status"].strip().lower())

            crops = query.all()
            for c in crops:
                farmer = c.farmer
                records.append({
                    "crop_id": c.id,
                    "farmer_name": farmer.full_name if farmer else "",
                    "district": farmer.district if farmer else "",
                    "crop_name": c.name,
                    "variety": c.variety or "",
                    "plot_name": c.plot_name or "",
                    "area": c.area,
                    "area_unit": c.area_unit,
                    "sowing_date": str(c.sowing_date),
                    "expected_harvest_date": str(c.expected_harvest_date) if c.expected_harvest_date else "",
                    "growth_stage": c.growth_stage,
                    "status": c.status,
                })

        elif mod == "expenses":
            query = db.query(Expense).join(User, Expense.farmer_id == User.id)
            if f.get("category") and f["category"].lower() != "all":
                query = query.filter(Expense.category == f["category"].strip())
            if f.get("district") and f["district"].lower() != "all":
                query = query.filter(func.lower(User.district) == f["district"].strip().lower())

            expenses = query.all()
            for e in expenses:
                farmer = e.farmer
                crop = e.crop
                records.append({
                    "expense_id": e.id,
                    "farmer_name": farmer.full_name if farmer else "",
                    "district": farmer.district if farmer else "",
                    "crop_name": crop.name if crop else "General",
                    "category": e.category,
                    "amount": e.amount,
                    "expense_date": str(e.expense_date),
                    "description": e.description or "",
                    "vendor": e.vendor or "",
                })

        elif mod == "harvest":
            query = db.query(HarvestRecord).join(User, HarvestRecord.farmer_id == User.id)
            if f.get("district") and f["district"].lower() != "all":
                query = query.filter(func.lower(User.district) == f["district"].strip().lower())

            harvests = query.all()
            for h in harvests:
                farmer = h.farmer
                crop = h.crop
                records.append({
                    "harvest_id": h.id,
                    "farmer_name": farmer.full_name if farmer else "",
                    "district": farmer.district if farmer else "",
                    "crop_name": crop.name if crop else "",
                    "harvest_date": str(h.harvest_date),
                    "quantity": h.quantity,
                    "unit": h.quantity_unit,
                    "revenue": h.total_revenue,
                    "price_per_unit": h.selling_price or 0.0,
                    "sold_to": h.buyer_name or "",
                    "quality_grade": getattr(h, "grade", "") or "",
                })

        elif mod == "activities":
            query = db.query(FarmActivity).join(User, FarmActivity.farmer_id == User.id)
            if f.get("district") and f["district"].lower() != "all":
                query = query.filter(func.lower(User.district) == f["district"].strip().lower())

            acts = query.all()
            for a in acts:
                farmer = a.farmer
                crop = a.crop
                records.append({
                    "activity_id": a.id,
                    "farmer_name": farmer.full_name if farmer else "",
                    "district": farmer.district if farmer else "",
                    "crop_name": crop.name if crop else "",
                    "activity_type": a.activity_type,
                    "activity_date": str(a.activity_date),
                    "cost": a.cost or 0.0,
                    "description": a.description or "",
                })

        elif mod == "overview":
            overview_dict = cls.get_system_overview(db, admin)
            records = [overview_dict]

        else:
            raise ValueError(f"Unsupported export module: {module}")

        # Generate serialized data in requested format
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agrisaathi_{mod}_{timestamp_str}.{fmt}"

        if fmt == "csv":
            df = pd.DataFrame(records)
            # Use utf-8-sig BOM so Devanagari (Marathi/Hindi) opens properly in Excel
            csv_buf = df.to_csv(index=False, encoding="utf-8-sig")
            data_bytes = csv_buf.encode("utf-8-sig")
            mime_type = "text/csv"

        elif fmt == "xlsx":
            df = pd.DataFrame(records)
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=mod.capitalize()[:30], index=False)
            data_bytes = excel_buf.getvalue()
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        elif fmt == "json":
            json_str = json.dumps(records, indent=2, ensure_ascii=False, default=str)
            data_bytes = json_str.encode("utf-8")
            mime_type = "application/json"

        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        # Log export event in Admin Audit Log
        cls.log_action(
            db=db,
            admin=admin,
            action="EXPORT_DATA",
            resource_type=mod,
            details={
                "format": fmt,
                "record_count": len(records),
                "filters": f,
                "file_size_bytes": len(data_bytes),
            },
        )

        return data_bytes, filename, mime_type
