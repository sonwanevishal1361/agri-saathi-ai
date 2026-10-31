"""Central agriculture theme, accessibility styling, and mobile responsiveness helper."""

import streamlit as st


def inject_custom_theme():
    """Inject high-contrast, accessible, mobile-first CSS styles for AgriSaathi AI."""
    st.markdown(
        """
        <style>
        /* ---------------- ROOT & ACCESSIBILITY ---------------- */
        :root {
            --agri-green-dark: #1b5e20;
            --agri-green-primary: #2e7d32;
            --agri-green-medium: #4caf50;
            --agri-green-light: #e8f5e9;
            --agri-green-subtle: #f1f8f1;
            --agri-earth-brown: #5d4037;
            --agri-text-dark: #142814;
            --agri-text-muted: #3e523e;
            --agri-card-bg: #ffffff;
            --agri-border: #c8e6c9;
            --agri-border-strong: #81c784;
            --agri-danger: #c62828;
            --agri-danger-bg: #ffebee;
            --agri-success: #2e7d32;
            --agri-success-bg: #e8f5e9;
            --agri-warn: #e65100;
            --agri-warn-bg: #fff3e0;
        }

        /* Base Typography for Outdoor Readability */
        html, body, [class*="css"] {
            font-size: 16px;
            color: var(--agri-text-dark);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Devanagari", sans-serif;
        }

        /* ---------------- LARGE TOUCH TARGETS (Min 48px) ---------------- */
        .stButton > button {
            min-height: 48px !important;
            padding: 10px 18px !important;
            font-size: 1.02rem !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            border: 1px solid var(--agri-border-strong) !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
            transition: all 0.15s ease-in-out !important;
        }

        .stButton > button:hover {
            border-color: var(--agri-green-primary) !important;
            background-color: var(--agri-green-subtle) !important;
            transform: translateY(-1px);
        }

        .stButton > button:active {
            transform: translateY(1px);
        }

        /* Primary Call-to-Action Buttons */
        div[data-testid="stButton"] button[kind="primary"],
        .stButton > button.agri-btn-primary {
            background-color: var(--agri-green-primary) !important;
            color: #ffffff !important;
            border: none !important;
            font-size: 1.08rem !important;
            box-shadow: 0 3px 8px rgba(46, 125, 50, 0.28) !important;
        }

        /* Form Inputs & Selectboxes - High Contrast */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            min-height: 48px !important;
            font-size: 1rem !important;
            border-radius: 8px !important;
            border: 1.5px solid #a5d6a7 !important;
            color: var(--agri-text-dark) !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--agri-green-primary) !important;
            box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.2) !important;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: var(--agri-card-bg);
            border: 1.5px solid var(--agri-border);
            border-radius: 12px;
            padding: 14px 16px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }

        div[data-testid="stMetricLabel"] p {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: var(--agri-text-muted) !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: var(--agri-green-dark) !important;
        }

        /* ---------------- CUSTOM AGRICULTURAL WIDGETS ---------------- */
        .top-navbar-card {
            background: #ffffff;
            border: 1.5px solid #a5d6a7;
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 14px;
            box-shadow: 0 2px 6px rgba(27, 94, 32, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }

        .farmer-welcome-banner {
            background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 70%, #388e3c 100%);
            color: #ffffff;
            border-radius: 16px;
            padding: 22px 24px;
            margin-bottom: 22px;
            box-shadow: 0 6px 18px rgba(27, 94, 32, 0.16);
            border: 1.5px solid #43a047;
        }

        .farmer-welcome-title {
            margin: 0;
            color: #ffffff;
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: -0.3px;
        }

        .farmer-welcome-sub {
            margin: 6px 0 0 0;
            color: #e8f5e9;
            font-size: 1.02rem;
            font-weight: 500;
        }

        .farmer-badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.35);
            color: #ffffff;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .action-card-box {
            background: #ffffff;
            border: 1.5px solid #c8e6c9;
            border-radius: 14px;
            padding: 18px 14px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            transition: all 0.2s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .action-card-box:hover {
            border-color: #2e7d32;
            box-shadow: 0 4px 12px rgba(46,125,50,0.12);
            transform: translateY(-2px);
        }

        .action-card-icon {
            font-size: 2.2rem;
            margin-bottom: 8px;
            display: block;
        }

        .action-card-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: #1b5e20;
            margin: 0 0 4px 0;
            line-height: 1.3;
        }

        .action-card-desc {
            font-size: 0.84rem;
            color: #4b634b;
            margin: 0 0 12px 0;
            line-height: 1.35;
            flex-grow: 1;
        }

        .weather-farmer-card {
            background: #ffffff;
            border: 2px solid #a5d6a7;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 22px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.04);
        }

        .weather-guidance-box {
            background: #f7faf7;
            border-left: 5px solid #2e7d32;
            border-radius: 6px;
            padding: 12px 14px;
            margin-top: 14px;
            font-size: 0.95rem;
            color: #1b3b1b;
            line-height: 1.5;
        }

        .weather-guidance-box.warn {
            background: #fff8f8;
            border-left-color: #d32f2f;
            color: #5f1515;
        }

        .crop-farmer-card {
            background: #ffffff;
            border: 1.5px solid #c8e6c9;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            transition: all 0.15s ease;
        }

        .crop-farmer-card:hover {
            border-color: #81c784;
        }

        .crop-care-tip {
            background: #eef7ee;
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 10px;
            font-size: 0.88rem;
            color: #1b5e20;
            border-left: 3px solid #4caf50;
        }

        .mandi-preview-box {
            background: #ffffff;
            border: 1.5px solid #c8e6c9;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }

        .mandi-preview-box:hover {
            border-color: #2e7d32;
            background: #fcfdfc;
        }

        .ai-search-banner {
            background: linear-gradient(135deg, #f1f8f1 0%, #e8f5e9 100%);
            border: 2px solid #a5d6a7;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 22px;
            box-shadow: 0 3px 10px rgba(46,125,50,0.06);
        }

        .action-tile-btn {
            display: block;
            background: linear-gradient(135deg, #ffffff, #f4fbf4);
            border: 2px solid #a5d6a7;
            border-radius: 14px;
            padding: 18px 16px;
            text-align: center;
            text-decoration: none;
            color: var(--agri-text-dark);
            box-shadow: 0 3px 8px rgba(0,0,0,0.04);
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .action-tile-btn:hover {
            border-color: var(--agri-green-primary);
            background: #e8f5e9;
            transform: translateY(-2px);
        }

        .weather-spray-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1rem;
            margin-top: 6px;
        }

        .spray-ok {
            background-color: #e8f5e9;
            color: #1b5e20;
            border: 2px solid #66bb6a;
        }

        .spray-warn {
            background-color: #ffebee;
            color: #b71c1c;
            border: 2px solid #ef5350;
        }

        /* Empty state cards */
        .empty-state-box {
            text-align: center;
            padding: 30px 20px;
            background: #ffffff;
            border: 2px dashed #a5d6a7;
            border-radius: 14px;
            margin: 15px 0;
        }

        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 10px;
        }

        /* ---------------- MOBILE RESPONSIVE TWEAKS (~360px) ---------------- */
        @media (max-width: 600px) {
            html, body, [class*="css"] {
                font-size: 17px;
            }
            .stButton > button {
                min-height: 52px !important;
                font-size: 1.05rem !important;
                width: 100% !important;
            }
            div[data-testid="stMetricValue"] {
                font-size: 1.4rem !important;
            }
            .top-navbar-card {
                flex-direction: column;
                align-items: stretch;
                text-align: center;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

