"""Olympic-style Mandi Podium Cards for AgriSaathi AI.

Displays the top 3 APMC markets (🥇 Gold, 🥈 Silver, 🥉 Bronze) with transport cost
deduction and net return highlight in harvest gold and forest green.
"""

import textwrap
from typing import Any, Dict, List
import streamlit as st
from utils.formatting import format_inr
from utils.language import t


def render_podium_cards(
    top_records: List[Dict[str, Any]],
    selling_qty: float = 50.0,
    lang: str = "mr",
):
    """Render Olympic-style podium cards for top 3 APMC markets."""
    if not top_records:
        return

    top_3 = top_records[:3]
    st.markdown(
        textwrap.dedent(f"""
        <div style="margin: 20px 0 14px 0;">
            <h3 style="color: #0f3822; font-size: 1.4rem; font-weight: 800; margin: 0; display: flex; align-items: center; gap: 8px;">
                🏆 <span>{t('mandi_top_markets', lang) if t('mandi_top_markets', lang) != 'mandi_top_markets' else 'सर्वोच्च ३ बाजार समित्या (Top 3 APMC Markets)'}</span>
            </h3>
            <p style="color: #4b634b; font-size: 0.92rem; margin: 4px 0 0 0; font-weight: 600;">
                {t('mandi_podium_subtitle', lang) if t('mandi_podium_subtitle', lang) != 'mandi_podium_subtitle' else 'वाहतूक खर्च वजा जाता शेतकऱ्यांसाठी सर्वोत्तम निव्वळ नफा देणाऱ्या बाजार समित्या'}
            </p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    cols = st.columns(len(top_3))
    # If 3 records, podium order: 2nd (Silver, left), 1st (Gold, center), 3rd (Bronze, right)
    col_mapping = [cols[1], cols[0], cols[2]] if len(top_3) == 3 else cols

    medals = [
        {"emoji": "🥇 1st", "title": "सुवर्ण (Gold)", "cls": "podium-1st", "border": "#f9a825", "bg": "linear-gradient(180deg, #fffde7 0%, #ffffff 100%)"},
        {"emoji": "🥈 2nd", "title": "रौप्य (Silver)", "cls": "podium-2nd", "border": "#b0bec5", "bg": "#ffffff"},
        {"emoji": "🥉 3rd", "title": "कांस्य (Bronze)", "cls": "podium-3rd", "border": "#bcaaa4", "bg": "#ffffff"},
    ]

    for idx, rec in enumerate(top_3):
        medal = medals[idx] if idx < len(medals) else medals[2]
        target_col = col_mapping[idx] if len(top_3) == 3 else cols[idx]

        m_market = rec.get("market", "APMC Market")
        m_dist_km = rec.get("distance_km", 0.0)
        m_district = rec.get("district", "")
        m_modal = float(rec.get("modal_price", 0.0))
        m_trans = float(rec.get("transport_cost_per_qtl", 0.0))
        m_net = float(rec.get("estimated_net_price", m_modal))
        net_rev = float(rec.get("net_revenue", m_net * selling_qty))

        with target_col:
            is_gold = idx == 0
            gold_glow = "box-shadow: 0 12px 30px rgba(249, 168, 37, 0.22); transform: scale(1.02);" if is_gold else "box-shadow: var(--shadow-3d-card);"

            podium_html = textwrap.dedent(f"""
            <div class="podium-card {medal['cls']}" style="
                background: {medal['bg']};
                border: 2px solid {medal['border']};
                border-radius: 22px;
                padding: 20px 16px;
                text-align: center;
                margin-bottom: 14px;
                {gold_glow}
            ">
                <div style="font-size: 2.2rem; margin-bottom: 6px;">{medal['emoji']}</div>
                <div style="font-size: 0.8rem; font-weight: 800; color: #166534; text-transform: uppercase; letter-spacing: 0.05em;">
                    {medal['title']}
                </div>
                <h3 style="margin: 6px 0 2px 0; color: #0f3822; font-size: 1.35rem; font-weight: 800; line-height: 1.2;">
                    {m_market}
                </h3>
                <div style="font-size: 0.88rem; color: #4b634b; font-weight: 600; margin-bottom: 12px;">
                    📍 {m_district} • {m_dist_km} किमी
                </div>

                <div style="background: #f1f8f1; border-radius: 12px; padding: 10px; margin-bottom: 10px;">
                    <div style="font-size: 0.85rem; color: #4b634b; font-weight: 600;">
                        बाजार भाव (Modal): <strong>₹{m_modal:,.0f}</strong> / क्विंटल
                    </div>
                    <div style="font-size: 0.82rem; color: #c62828; font-weight: 700; margin-top: 2px;">
                        वाहतूक खर्च: -₹{m_trans:,.0f} / क्विंटल
                    </div>
                </div>

                <div class="podium-net-highlight" style="
                    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
                    color: #ffffff;
                    font-size: 1.2rem;
                    font-weight: 800;
                    padding: 10px;
                    border-radius: 14px;
                    margin-bottom: 10px;
                    box-shadow: 0 4px 12px rgba(27, 94, 32, 0.25);
                ">
                    💰 निव्वळ दर: ₹{m_net:,.0f} / क्विंटल
                </div>

                <div style="font-size: 0.88rem; color: #1b5e20; font-weight: 700; padding: 4px 0;">
                    {selling_qty:.0f} क्विंटल निव्वळ नफा: <span style="font-size: 1.05rem; color: #0f3822; font-weight: 800;">{format_inr(net_rev)}</span>
                </div>
            </div>
            """).strip()
            st.markdown(podium_html, unsafe_allow_html=True)

