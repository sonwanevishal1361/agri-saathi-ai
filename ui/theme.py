"""Central agriculture theme, accessibility styling, and mobile responsiveness helper for AgriSaathi AI."""

import textwrap
import streamlit as st


def clean_html(html_str: str) -> str:
    """Strip all leading/trailing whitespace from every line to prevent Markdown code-block parsing."""
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())


def inject_custom_theme():
    """Inject high-contrast, accessible, mobile-first CSS styles for AgriSaathi AI."""
    st.markdown(
        textwrap.dedent("""
        <style>
        /* ---------------- GOOGLE FONTS ---------------- */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Nunito:wght@400;600;700;800&family=Poppins:wght@500;600;700;800&display=swap');

        /* ---------------- ROOT DESIGN TOKENS: DIGITAL KRISHI PREMIUM ---------------- */
        :root {
            /* Natural Agricultural Palette */
            --agri-deep-forest: #1b5e20;
            --agri-leaf: #2e7d32;
            --agri-fresh-lime: #8bc34a;
            --agri-harvest-gold: #f9a825;
            --agri-sunrise-orange: #ff8f00;
            --agri-soil-brown: #6d4c41;
            --agri-sky-blue: #4fc3f7;
            --agri-cream: #fff8e1;
            --agri-ink: #1f2a1f;

            /* Ambient Accents & Surface Tokens */
            --agri-green-dark: #1b5e20;
            --agri-green-primary: #2e7d32;
            --agri-emerald: #1e6b3e;
            --agri-green-medium: #4caf50;
            --agri-green-light: #e8f5e9;
            --agri-sage-soft: #edf7f0;
            --agri-green-subtle: #f1f8f1;
            --agri-gold-amber: #f59e0b;
            --agri-gold-light: #fff8e1;
            --agri-cream-bg: #f9fbf9;
            --agri-surface-card: #ffffff;

            /* High Contrast Outdoor Typography */
            --agri-text-dark: #122a1a;
            --agri-text-strong: #1f2a1f;
            --agri-text-muted: #3d5a45;
            --agri-text-subtle: #617b68;

            /* Soft Layered 3D Depth & Glass Borders */
            --agri-card-bg: #ffffff;
            --agri-border: #d4ebd9;
            --agri-border-strong: #81c784;
            --agri-border-focus: #1b5e20;

            /* Multi-layer Drop Shadows */
            --shadow-3d-card: 0 1px 2px rgba(15, 56, 34, 0.04), 0 8px 24px -4px rgba(15, 56, 34, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.85);
            --shadow-3d-hover: 0 4px 8px rgba(15, 56, 34, 0.06), 0 16px 36px -6px rgba(15, 56, 34, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.9);
            --shadow-glass: 0 8px 32px 0 rgba(15, 56, 34, 0.09);

            /* Optional Night Field Dark Palette */
            --agri-night-bg: #0b1b10;
            --agri-night-surface: #122818;
            --agri-night-border: rgba(139, 195, 74, 0.25);
            --agri-night-text: #e8f5e9;

            /* Status Alerts */
            --agri-danger: #c62828;
            --agri-danger-bg: #ffebee;
            --agri-success: #2e7d32;
            --agri-success-bg: #e8f5e9;
            --agri-warn: #e65100;
            --agri-warn-bg: #fff3e0;
        }

        /* ---------------- STREAMLIT CHROME CLEANUP ---------------- */
        #MainMenu,
        footer,
        [data-testid="stDecoration"],
        [data-testid="stToolbar"],
        [data-testid="stStatusWidget"],
        .stDeployButton {
            display: none !important;
            visibility: hidden !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
            z-index: 100 !important;
        }

        /* ---------------- BASE TYPOGRAPHY (Outdoor Readable 18px) ---------------- */
        html, body, [class*="css"] {
            font-size: 18px !important;
            color: var(--agri-text-strong) !important;
            font-family: 'Noto Sans Devanagari', 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            background-color: var(--agri-cream-bg);
            -webkit-font-smoothing: antialiased;
        }

        /* Top level Streamlit container spacing & max width */
        .block-container {
            padding-top: 1.0rem !important;
            padding-bottom: 96px !important; /* Space for fixed bottom navigation */
            max-width: 1280px !important;
        }

        /* ---------------- FLOATING GLASS HEADER ---------------- */
        .agri-glass-header {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(200, 230, 213, 0.75);
            border-radius: 20px;
            padding: 14px 20px;
            margin-bottom: 18px;
            box-shadow: 0 8px 24px -4px rgba(15, 56, 34, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }

        /* ---------------- HERO BANNER WITH 3D DEPTH ---------------- */
        .agri-hero-banner {
            background: linear-gradient(135deg, #0f3822 0%, #1b5e20 45%, #2e7d32 85%, #388e3c 100%);
            color: #ffffff;
            border-radius: 22px;
            padding: 24px 26px;
            margin-bottom: 22px;
            box-shadow: 0 14px 34px -6px rgba(15, 56, 34, 0.22), 0 2px 6px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border: 1.5px solid rgba(255, 255, 255, 0.22);
            position: relative;
            overflow: hidden;
        }
        .agri-hero-banner::after {
            content: '';
            position: absolute;
            top: -40px;
            right: -40px;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(249, 168, 37, 0.25) 0%, rgba(255,255,255,0) 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        /* ---------------- ERGONOMIC TOUCH TARGETS (MINIMUM 56px) ---------------- */
        .stButton > button {
            min-height: 56px !important;
            min-width: 56px !important;
            padding: 12px 22px !important;
            font-size: 1.08rem !important;
            font-weight: 700 !important;
            border-radius: 16px !important;
            border: 1.5px solid var(--agri-border) !important;
            background: #ffffff !important;
            color: var(--agri-text-strong) !important;
            box-shadow: 0 2px 6px rgba(15, 56, 34, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            touch-action: manipulation;
        }

        .stButton > button:hover {
            border-color: var(--agri-green-primary) !important;
            background: var(--agri-sage-soft) !important;
            color: var(--agri-green-dark) !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(15, 56, 34, 0.1) !important;
        }

        .stButton > button:active {
            transform: translateY(1px);
            box-shadow: 0 1px 3px rgba(15, 56, 34, 0.08) !important;
        }

        /* Primary Call-to-Action Buttons */
        div[data-testid="stButton"] button[kind="primary"],
        .stButton > button.agri-btn-primary {
            background: linear-gradient(135deg, #1e6b3e 0%, #134e2c 100%) !important;
            color: #ffffff !important;
            border: 1.5px solid #0f3822 !important;
            font-size: 1.12rem !important;
            font-weight: 800 !important;
            box-shadow: 0 6px 18px rgba(30, 107, 62, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            background: linear-gradient(135deg, #165330 0%, #0d3b20 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 8px 24px rgba(30, 107, 62, 0.4) !important;
            transform: translateY(-2px);
        }

        /* Form Inputs & Selectboxes - 56px Touch Target */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            min-height: 56px !important;
            font-size: 1.05rem !important;
            border-radius: 14px !important;
            border: 1.5px solid #b7dfc3 !important;
            color: var(--agri-text-strong) !important;
            background-color: #ffffff !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
            transition: all 0.2s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--agri-emerald) !important;
            box-shadow: 0 0 0 3.5px rgba(30, 107, 62, 0.2) !important;
        }

        /* ---------------- 3D LAYERED METRIC CARDS ---------------- */
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid rgba(200, 230, 213, 0.7);
            border-radius: 18px;
            padding: 18px 20px !important;
            box-shadow: var(--shadow-3d-card);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-3d-hover);
        }

        div[data-testid="stMetricLabel"] p {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: var(--agri-text-muted) !important;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.95rem !important;
            font-weight: 800 !important;
            color: var(--agri-deep-forest) !important;
        }

        /* ---------------- STREAMLIT TABS SEGMENTED PILLS ---------------- */
        div[data-baseweb="tab-list"] {
            background: #edf7f0;
            padding: 6px;
            border-radius: 18px;
            gap: 6px;
            border: 1px solid #c8e6d5;
            margin-bottom: 16px;
        }
        div[data-baseweb="tab"] {
            border-radius: 14px !important;
            padding: 10px 18px !important;
            font-weight: 700 !important;
            font-size: 1.02rem !important;
            color: var(--agri-text-muted) !important;
            background: transparent !important;
            border: none !important;
            transition: all 0.2s ease;
        }
        div[data-baseweb="tab"][aria-selected="true"] {
            background: #ffffff !important;
            color: var(--agri-deep-forest) !important;
            box-shadow: 0 4px 12px rgba(15, 56, 34, 0.1) !important;
        }

        /* ---------------- EXPANDERS & CONTAINERS ---------------- */
        div[data-testid="stExpander"] {
            border: 1px solid #d4ebd9 !important;
            border-radius: 18px !important;
            box-shadow: 0 2px 8px rgba(15, 56, 34, 0.04) !important;
            background: #ffffff !important;
            overflow: hidden !important;
            margin-bottom: 14px !important;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 700 !important;
            color: var(--agri-deep-forest) !important;
            padding: 14px 18px !important;
        }

        /* ---------------- FIXED BOTTOM NAVIGATION BAR ---------------- */
        .agri-bottom-nav-spacer {
            height: 80px;
        }

        /* ---------------- SINGLE NAVIGATION BAR ARCHITECTURE ---------------- */
        /* On Desktop (width >= 769px): SHOW top desktop bar, HIDE bottom thumb bar */
        @media (min-width: 769px) {
            .st-key-desktop_nav_container {
                display: block !important;
            }
            .st-key-bottom_nav_container,
            .agri-bottom-nav-container,
            .agri-bottom-nav-spacer {
                display: none !important;
            }
        }

        /* On Mobile (width <= 768px): HIDE top desktop bar, SHOW fixed bottom thumb bar */
        @media (max-width: 768px) {
            .st-key-desktop_nav_container,
            .agri-desktop-nav {
                display: none !important;
            }
            .st-key-bottom_nav_container {
                display: block !important;
                position: fixed !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                z-index: 999999 !important;
                background: rgba(255, 255, 255, 0.96) !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                border-top: 1.5px solid #a5d6a7 !important;
                padding: 6px 8px 14px 8px !important;
                box-shadow: 0 -8px 24px rgba(15, 56, 34, 0.12) !important;
            }
            .st-key-bottom_nav_container div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 4px !important;
                align-items: center !important;
                justify-content: space-between !important;
            }
            .st-key-bottom_nav_container div[data-testid="stColumn"] {
                width: auto !important;
                min-width: 0 !important;
                flex: 1 1 0 !important;
            }
            .st-key-bottom_nav_container button {
                padding: 6px 2px !important;
                min-height: 48px !important;
                font-size: 0.8rem !important;
                border-radius: 12px !important;
                white-space: nowrap !important;
            }
            .st-key-bottom_nav_container div[data-testid="stColumn"]:nth-child(3) button {
                background: linear-gradient(135deg, #f9a825 0%, #ff8f00 100%) !important;
                color: #142814 !important;
                border: 2px solid #ffffff !important;
                font-weight: 800 !important;
                font-size: 0.88rem !important;
                box-shadow: 0 4px 12px rgba(249, 168, 37, 0.45) !important;
                transform: translateY(-4px) !important;
            }
        }

        .agri-more-drawer {
            background: #fff8e1;
            border: 1.5px solid #f9a825;
            border-radius: 18px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes slideUp {
            from { transform: translateY(24px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        /* ---------------- PREMIUM AGRITECH ACTION TILES ---------------- */
        .agri-action-card {
            background: #ffffff;
            border-radius: 20px;
            border: 1.5px solid #d4ebd9;
            padding: 20px 18px 16px 18px;
            margin-bottom: 8px;
            box-shadow: var(--shadow-3d-card);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }
        .agri-action-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-3d-hover);
            border-color: #81c784;
        }
        .agri-action-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
            margin-top: 6px;
        }

        /* ---------------- 3D TILT EFFECT ---------------- */
        .tilt-card {
            background: #ffffff;
            border-radius: 20px;
            border: 1px solid #d4ebd9;
            box-shadow: var(--shadow-3d-card);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            transform-style: preserve-3d;
            perspective: 800px;
        }

        .tilt-card:hover {
            transform: perspective(800px) rotateX(1deg) rotateY(-1deg) translateY(-4px);
            box-shadow: var(--shadow-3d-hover) !important;
            border-color: #a5d6a7;
        }

        /* Step Pulse animation for current growth stage */
        @keyframes stepPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); box-shadow: 0 0 14px rgba(249, 168, 37, 0.7); }
            100% { transform: scale(1); }
        }
        .step-pulse > div:first-child {
            animation: stepPulse 2s infinite ease-in-out;
        }

        /* ---------------- CSS WEATHER ANIMATIONS ---------------- */
        /* Sun */
        .anim-sun {
            position: relative;
            width: 54px;
            height: 54px;
        }
        .sun-core {
            width: 38px;
            height: 38px;
            background: radial-gradient(circle, #fbc02d 0%, #f57f17 100%);
            border-radius: 50%;
            position: absolute;
            top: 8px;
            left: 8px;
            box-shadow: 0 0 18px rgba(251, 192, 45, 0.85);
        }
        .sun-rays {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            border: 3px dashed #f57f17;
            animation: spin 12s linear infinite;
        }
        @keyframes spin {
            100% { transform: rotate(360deg); }
        }

        /* Rain */
        .anim-cloud {
            position: relative;
            width: 60px;
            height: 50px;
        }
        .cloud-body {
            width: 48px;
            height: 26px;
            background: linear-gradient(180deg, #b0bec5 0%, #78909c 100%);
            border-radius: 20px;
            position: relative;
            box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        }
        .cloud-body::before {
            content: '';
            position: absolute;
            top: -14px;
            left: 8px;
            width: 26px;
            height: 26px;
            background: #78909c;
            border-radius: 50%;
        }
        .rain-drops {
            position: absolute;
            top: 28px;
            left: 10px;
            display: flex;
            gap: 9px;
        }
        .drop {
            width: 3.5px;
            height: 12px;
            background: #29b6f6;
            border-radius: 2px;
            animation: rainFall 0.75s linear infinite;
        }
        .d2 { animation-delay: 0.25s; }
        .d3 { animation-delay: 0.5s; }
        @keyframes rainFall {
            0% { transform: translateY(0); opacity: 1; }
            100% { transform: translateY(14px); opacity: 0; }
        }

        /* Cloud Float */
        .anim-sun-cloud {
            position: relative;
            width: 60px;
            height: 50px;
        }
        .sun-glow {
            width: 30px;
            height: 30px;
            background: radial-gradient(circle, #fbc02d 0%, #f57f17 100%);
            border-radius: 50%;
            position: absolute;
            top: 2px;
            left: 4px;
            box-shadow: 0 0 12px #fbc02d;
        }
        .cloud-float {
            width: 48px;
            height: 24px;
            background: #cfd8dc;
            border-radius: 20px;
            position: absolute;
            bottom: 4px;
            right: 2px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            animation: cloudWiggle 3s ease-in-out infinite alternate;
        }
        @keyframes cloudWiggle {
            0% { transform: translateX(0); }
            100% { transform: translateX(7px); }
        }

        /* ---------------- WHATSAPP / MODERN CHAT BUBBLES ---------------- */
        .chat-bubble-row {
            display: flex;
            margin-bottom: 16px;
            width: 100%;
        }
        .chat-row-user {
            justify-content: flex-end;
        }
        .chat-row-assistant {
            justify-content: flex-start;
        }
        .chat-bubble {
            max-width: 82%;
            padding: 16px 20px;
            font-size: 1.05rem;
            line-height: 1.6;
            box-shadow: 0 4px 14px rgba(15, 56, 34, 0.06);
            position: relative;
        }
        .chat-bubble-user {
            background: linear-gradient(135deg, #dcf8c6 0%, #c8e6c9 100%);
            color: #122a1a;
            border-radius: 22px 22px 4px 22px;
            border: 1.5px solid #a5d6a7;
        }
        .chat-bubble-assistant {
            background: #ffffff;
            color: #122a1a;
            border-radius: 22px 22px 22px 4px;
            border: 1.5px solid #d4ebd9;
            box-shadow: var(--shadow-3d-card);
        }
        .chat-avatar {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            background: #e8f5e9;
            border: 2px solid #81c784;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.65rem;
            margin-right: 12px;
            flex-shrink: 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }

        /* ---------------- PODIUM STYLING FOR MANDI ---------------- */
        .podium-container {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 14px;
            margin: 22px 0;
            padding: 12px;
        }
        .podium-card {
            background: #ffffff;
            border-radius: 22px;
            padding: 18px 16px;
            text-align: center;
            box-shadow: var(--shadow-3d-card);
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.25s ease;
        }
        .podium-card:hover {
            transform: translateY(-4px);
        }
        .podium-1st {
            border: 2.5px solid #f9a825;
            background: linear-gradient(180deg, #fffde7 0%, #ffffff 100%);
            min-height: 250px;
            flex: 1.15;
            transform: scale(1.03);
            box-shadow: 0 12px 30px rgba(249, 168, 37, 0.22);
        }
        .podium-2nd {
            border: 2px solid #b0bec5;
            min-height: 220px;
            flex: 1;
        }
        .podium-3rd {
            border: 2px solid #bcaaa4;
            min-height: 200px;
            flex: 1;
        }
        .podium-medal {
            font-size: 2.3rem;
            margin-bottom: 4px;
        }
        .podium-net-highlight {
            background: linear-gradient(135deg, #1e6b3e 0%, #155730 100%);
            color: #ffffff;
            font-size: 1.25rem;
            font-weight: 800;
            padding: 8px 12px;
            border-radius: 12px;
            margin: 8px 0;
            box-shadow: 0 4px 10px rgba(30, 107, 62, 0.25);
        }

        /* ---------------- LOADING SKELETON & EMPTY STATES ---------------- */
        .skeleton-box {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 16px;
            min-height: 85px;
            margin-bottom: 14px;
        }
        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        .empty-state-box {
            text-align: center;
            padding: 38px 24px;
            background: #ffffff;
            border: 2px dashed #a5d6a7;
            border-radius: 22px;
            margin: 20px 0;
            box-shadow: var(--shadow-3d-card);
        }
        .empty-state-icon {
            font-size: 3.8rem;
            margin-bottom: 14px;
        }

        /* ---------------- MOBILE RESPONSIVE TWEAKS (360px & 390px) ---------------- */
        @media (max-width: 600px) {
            html, body, [class*="css"] {
                font-size: 17px !important;
            }
            .block-container {
                padding-left: 0.65rem !important;
                padding-right: 0.65rem !important;
                padding-bottom: 104px !important;
            }
            .agri-glass-header {
                padding: 12px 14px !important;
            }
            .agri-hero-banner {
                padding: 18px 16px !important;
            }
            .stButton > button {
                min-height: 56px !important;
                font-size: 1.05rem !important;
                width: 100% !important;
            }
            .chat-bubble {
                max-width: 90% !important;
            }
            .podium-container {
                flex-direction: column;
                align-items: stretch;
            }
            .podium-1st {
                transform: scale(1);
                order: -1;
            }
        }
        </style>
        """).strip(),
        unsafe_allow_html=True,
    )
