"""Growth-stage progress tracker (6 steps) with days-to-harvest counter for farmer crop cards."""

from datetime import date
from typing import Any
import streamlit as st
from utils.formatting import format_date
from utils.language import t, localize_unit
from ui.theme import clean_html


def get_stage_index(stage_name: str) -> int:
    """Map growth stage string to 0..5 progressive index."""
    s = (stage_name or "").lower()
    if any(k in s for k in ["sow", "पेरणी", "बुवाई", "nursery"]):
        return 0
    if any(k in s for k in ["germin", "emerg", "उगवण", "अंकुरण"]):
        return 1
    if any(k in s for k in ["veg", "tiller", "branch", "वाढ", "फुटवे"]):
        return 2
    if any(k in s for k in ["flower", "bud", "square", "फुलोरा", "कळ्या", "फूल"]):
        return 3
    if any(k in s for k in ["pod", "boll", "grain", "fruit", "शेंग", "दाणे", "बोंड", "फल"]):
        return 4
    if any(k in s for k in ["matur", "harvest", "ready", "पक्व", "कापणी", "काढणी", "कटाई"]):
        return 5
    return 2  # default vegetative


def get_days_to_harvest_text(expected_date: Any, lang: str = "mr") -> str:
    """Calculate and format days to harvest counter."""
    if not expected_date:
        return "-- दिवस" if lang == "mr" else ("-- दिन" if lang == "hi" else "-- days")

    try:
        today = date.today()
        if hasattr(expected_date, "date"):
            exp = expected_date.date()
        else:
            exp = expected_date

        diff = (exp - today).days
        if diff > 0:
            if lang == "mr":
                return f"⏳ {diff} दिवस शिल्लक"
            elif lang == "hi":
                return f"⏳ {diff} दिन शेष"
            else:
                return f"⏳ {diff} days left"
        elif diff == 0:
            if lang == "mr":
                return "🚜 आजच काढणी करा"
            elif lang == "hi":
                return "🚜 आज ही कटाई करें"
            else:
                return "🚜 Harvest Today"
        else:
            if lang == "mr":
                return "🌾 काढणीस तयार"
            elif lang == "hi":
                return "🌾 कटाई के लिए तैयार"
            else:
                return "🌾 Ready for Harvest"
    except Exception:
        return "-- दिवस" if lang == "mr" else ("-- दिन" if lang == "hi" else "-- days")


def render_crop_tracker_card(
    crop: Any,
    crop_icon: str,
    care_tip: str,
    lang: str = "mr",
    on_click_key: str = "",
) -> bool:
    """Render crop card with 6-step plant growth pipeline and CSS 3D tilt."""
    current_idx = get_stage_index(crop.growth_stage)

    # 6 Growth Stages pipeline
    stages_data = [
        {"icon": "🌱", "mr": "पेरणी", "hi": "बुवाई", "en": "Sowing"},
        {"icon": "🌿", "mr": "उगवण", "hi": "अंकुरण", "en": "Sprout"},
        {"icon": "🪴", "mr": "वाढ", "hi": "बढ़वार", "en": "Growth"},
        {"icon": "🌸", "mr": "फुलोरा", "hi": "फूल", "en": "Flower"},
        {"icon": "🌾", "mr": "दाणे/शेंग", "hi": "दाने/फली", "en": "Grain/Pod"},
        {"icon": "🚜", "mr": "काढणी", "hi": "कटाई", "en": "Harvest"},
    ]

    # Build 6-step HTML tracker
    steps_html = []
    for i, stg in enumerate(stages_data):
        is_done = i < current_idx
        is_current = i == current_idx

        if is_current:
            step_bg = "#f9a825"
            step_border = "#e65100"
            step_color = "#142814"
            pulse_cls = "step-pulse"
        elif is_done:
            step_bg = "#2e7d32"
            step_border = "#1b5e20"
            step_color = "#ffffff"
            pulse_cls = ""
        else:
            step_bg = "#e8f5e9"
            step_border = "#c8e6c9"
            step_color = "#81c784"
            pulse_cls = ""

        label = stg.get(lang, stg["en"])
        steps_html.append(
            clean_html(f"""
            <div class="crop-stage-step {pulse_cls}" style="flex: 1; text-align: center; position: relative;">
                <div style="
                    width: 38px;
                    height: 38px;
                    margin: 0 auto;
                    border-radius: 50%;
                    background: {step_bg};
                    border: 2px solid {step_border};
                    color: {step_color};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.15rem;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
                ">
                    {stg['icon']}
                </div>
                <div style="font-size: 0.76rem; font-weight: { '800' if is_current else '600' }; color: { '#1b5e20' if is_current or is_done else '#78909c' }; margin-top: 4px; line-height: 1.1;">
                    {label}
                </div>
            </div>
            """)
        )

    pipeline_html = "".join(steps_html)
    sow_date_str = format_date(crop.sowing_date)
    harvest_date_str = format_date(crop.expected_harvest_date) if crop.expected_harvest_date else "--"
    days_left_badge = get_days_to_harvest_text(crop.expected_harvest_date, lang)
    localized_area_unit = localize_unit(crop.area_unit, lang)

    st.markdown(
        clean_html(f"""
        <div class="agri-crop-card tilt-card" style="
            background: #ffffff;
            border: 2px solid #a5d6a7;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 6px 20px rgba(46, 125, 50, 0.08);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        ">
            <!-- Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 48px; height: 48px; border-radius: 14px; background: #e8f5e9; border: 1.5px solid #a5d6a7; display: flex; align-items: center; justify-content: center; font-size: 2rem;">
                        {crop_icon}
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #1b5e20; font-size: 1.35rem; font-weight: 800;">{crop.name}</h4>
                        <span style="font-size: 0.88rem; color: #4b634b; font-weight: 600;">{crop.plot_name or ('शेताचा तुकडा' if lang == 'mr' else 'Plot')}</span>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                    <span style="background: #e8f5e9; color: #1b5e20; border: 1.5px solid #81c784; font-size: 0.82rem; font-weight: 700; padding: 4px 12px; border-radius: 20px;">
                        {crop.variety or 'Standard'}
                    </span>
                    <span style="background: #fff8e1; color: #b45309; border: 1px solid #fde68a; font-size: 0.8rem; font-weight: 800; padding: 3px 10px; border-radius: 12px;">
                        {days_left_badge}
                    </span>
                </div>
            </div>

            <!-- Key Specs in Pills -->
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px;">
                <span style="background: #fff8e1; border: 1.5px solid #ffe082; color: #6d4c41; padding: 5px 12px; border-radius: 12px; font-size: 0.88rem; font-weight: 700;">
                    📐 {crop.area} {localized_area_unit}
                </span>
                <span style="background: #f1f8f1; border: 1.5px solid #c8e6c9; color: #1b5e20; padding: 5px 12px; border-radius: 12px; font-size: 0.88rem; font-weight: 600;">
                    🌱 {t('sowing_date_lbl', lang)}: {sow_date_str}
                </span>
                <span style="background: #f1f8f1; border: 1.5px solid #c8e6c9; color: #1b5e20; padding: 5px 12px; border-radius: 12px; font-size: 0.88rem; font-weight: 600;">
                    🌾 {t('crop_expected_harvest', lang)} {harvest_date_str}
                </span>
            </div>

            <!-- 6-Stage Progress Tracker -->
            <div style="background: #fcfdfc; border: 1.5px solid #e0f2f1; border-radius: 16px; padding: 14px 8px; margin-bottom: 14px;">
                <div style="font-size: 0.85rem; font-weight: 800; color: #2e7d32; margin-bottom: 10px; padding-left: 8px;">
                    📈 वाढीची अवस्था (Stage Tracker - Step {current_idx + 1}/6):
                </div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 2px;">
                    {pipeline_html}
                </div>
            </div>

            <!-- Practical Care Tip -->
            <div style="
                background: #eef7ee;
                border-left: 4px solid #2e7d32;
                border-radius: 10px;
                padding: 12px 14px;
                font-size: 0.94rem;
                color: #1b5e20;
                line-height: 1.45;
                margin-bottom: 14px;
            ">
                💡 <strong>{t('crop_stage_care_lbl', lang)}</strong> {care_tip}
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    return st.button(
        f"🔍 {t('view_details', lang)}",
        key=on_click_key or f"btn_view_crop_{crop.id}",
        use_container_width=True,
    )
