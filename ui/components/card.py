"""High-contrast, rounded card components with soft organic shadows for Indian farmers."""

import textwrap
from typing import Optional
import streamlit as st


def render_card(
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    badge: Optional[str] = None,
    badge_color: str = "#2e7d32",
    badge_bg: str = "#e8f5e9",
    border_color: str = "#d4ebd9",
    background: str = "#ffffff",
    padding: str = "18px 20px",
    extra_class: str = "",
):
    """Render an accessible, rounded card container with warm borders and soft shadows."""
    badge_html = (
        f"""<span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {border_color}; """
        f"""padding: 4px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 700;">{badge}</span>"""
        if badge
        else ""
    )

    icon_html = f"""<span style="font-size: 1.8rem; margin-right: 12px; display: inline-flex; align-items: center;">{icon}</span>""" if icon else ""
    sub_html = f"""<p style="margin: 4px 0 0 0; color: #4b5563; font-size: 0.95rem; line-height: 1.4;">{subtitle}</p>""" if subtitle else ""

    html = textwrap.dedent(f"""
        <div class="agri-card tilt-card {extra_class}" style="
            background: {background};
            border: 1px solid {border_color};
            border-radius: 20px;
            padding: {padding};
            margin-bottom: 18px;
            box-shadow: 0 4px 16px -2px rgba(15, 56, 34, 0.06);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: {'10px' if (title or badge) else '0'}; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center;">
                    {icon_html}
                    <div>
                        <h3 style="margin: 0; color: #0b2316; font-size: 1.25rem; font-weight: 700; line-height: 1.3;">{title}</h3>
                        {sub_html}
                    </div>
                </div>
                {badge_html}
            </div>
        </div>
    """).strip()

    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: str,
    icon: str = "🌾",
    delta: Optional[str] = None,
    is_positive: bool = True,
    bg_color: str = "#ffffff",
):
    """Render an oversized, legible metric card tailored for outdoor sunlight reading."""
    delta_color = "#16a34a" if is_positive else "#dc2626"
    delta_arrow = "▲" if is_positive else "▼"
    delta_html = (
        f"""<div style="margin-top: 4px; font-size: 0.88rem; font-weight: 700; color: {delta_color};">"""
        f"""{delta_arrow} {delta}</div>"""
        if delta
        else ""
    )

    html = textwrap.dedent(f"""
        <div class="agri-metric-tile tilt-card" style="
            background: {bg_color};
            border: 1px solid #d4ebd9;
            border-radius: 20px;
            padding: 16px 20px;
            margin-bottom: 14px;
            box-shadow: 0 4px 16px -2px rgba(15, 56, 34, 0.06);
            display: flex;
            align-items: center;
            gap: 16px;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        ">
            <div style="
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                color: #166534;
                font-size: 1.8rem;
                min-width: 52px;
                height: 52px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #bbf7d0;
                flex-shrink: 0;
            ">
                {icon}
            </div>
            <div>
                <div style="font-size: 0.82rem; font-weight: 700; color: #4b5563; text-transform: uppercase; letter-spacing: 0.03em;">
                    {label}
                </div>
                <div style="font-size: 1.65rem; font-weight: 800; color: #0b2316; line-height: 1.2; margin-top: 2px;">
                    {value}
                </div>
                {delta_html}
            </div>
        </div>
    """).strip()

    st.markdown(html, unsafe_allow_html=True)
