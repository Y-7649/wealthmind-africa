"""
utils/styles.py
WealthMind Africa — Global CSS Injection

Injects premium CSS into every page. Call inject_global_styles() once
at the top of any Streamlit page to apply the full visual design system.

Design principles:
    - Intelligent, institutional, academic
    - Teal (#00C49F) as the primary accent
    - Dark backgrounds with subtle depth
    - Smooth, purposeful animations — nothing gratuitous
    - Inter typeface for professional readability
"""

import streamlit as st


def inject_global_styles():
    """
    Inject the complete WealthMind Africa CSS design system.
    Safe to call multiple times — browser deduplicates identical style blocks.
    """
    st.markdown(
        """
        <style>

        /* ── TYPOGRAPHY ─────────────────────────────────────────────────── */

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"], .stMarkdown, .stText {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                         'Segoe UI', sans-serif !important;
        }

        h1, h2, h3, h4 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
        }

        /* ── KEYFRAME ANIMATIONS ────────────────────────────────────────── */

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(18px); }
            to   { opacity: 1; transform: translateY(0);    }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to   { opacity: 1; }
        }

        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(20px); }
            to   { opacity: 1; transform: translateX(0);    }
        }

        @keyframes glowPulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(0,196,159,0); }
            50%       { box-shadow: 0 0 20px 4px rgba(0,196,159,0.12); }
        }

        @keyframes borderFade {
            0%, 100% { border-color: rgba(0,196,159,0.25); }
            50%       { border-color: rgba(0,196,159,0.6);  }
        }

        @keyframes gradientDrift {
            0%   { background-position: 0% 50%;   }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%;   }
        }

        @keyframes dotPulse {
            0%, 100% { transform: scale(1);   opacity: 1;   }
            50%       { transform: scale(1.4); opacity: 0.6; }
        }

        /* ── PAGE ENTRANCE ──────────────────────────────────────────────── */

        .main .block-container {
            animation: fadeInUp 0.45s cubic-bezier(0.22, 1, 0.36, 1);
            padding-top: 1.2rem !important;
        }

        /* ── METRIC CARDS ───────────────────────────────────────────────── */

        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #1C2333 0%, #161D2A 100%) !important;
            border: 1px solid #252D3D !important;
            border-radius: 12px !important;
            padding: 1.1rem 1.3rem !important;
            transition: transform 0.25s ease, box-shadow 0.25s ease,
                        border-color 0.25s ease !important;
            animation: fadeInUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-3px) !important;
            border-color: rgba(0,196,159,0.45) !important;
            box-shadow: 0 8px 30px rgba(0,196,159,0.1),
                        0 2px 8px rgba(0,0,0,0.3) !important;
        }

        [data-testid="stMetricValue"] {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        [data-testid="stMetricLabel"] {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.78rem !important;
            color: #8899AA !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
        }

        /* ── BUTTONS ────────────────────────────────────────────────────── */

        .stButton > button {
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            letter-spacing: 0.01em !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease,
                        background 0.2s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0,196,159,0.25) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #00C49F 0%, #00A07F 100%) !important;
            border: none !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #00D4AC 0%, #00B08C 100%) !important;
        }

        /* ── FORM INPUTS ────────────────────────────────────────────────── */

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input {
            border-radius: 8px !important;
            border: 1px solid #252D3D !important;
            background: #111620 !important;
            font-family: 'Inter', sans-serif !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stNumberInput"] input:focus {
            border-color: #00C49F !important;
            box-shadow: 0 0 0 3px rgba(0,196,159,0.12) !important;
        }

        /* ── SELECTBOX ──────────────────────────────────────────────────── */

        [data-testid="stSelectbox"] > div > div {
            border-radius: 8px !important;
            border: 1px solid #252D3D !important;
            background: #111620 !important;
            transition: border-color 0.2s ease !important;
        }

        [data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #00C49F !important;
        }

        /* ── DATE INPUT ─────────────────────────────────────────────────── */

        [data-testid="stDateInput"] input {
            border-radius: 8px !important;
            border: 1px solid #252D3D !important;
            background: #111620 !important;
        }

        /* ── EXPANDERS ──────────────────────────────────────────────────── */

        [data-testid="stExpander"] {
            border: 1px solid #252D3D !important;
            border-radius: 12px !important;
            background: #111620 !important;
            transition: border-color 0.25s ease !important;
            overflow: hidden !important;
        }

        [data-testid="stExpander"]:hover {
            border-color: rgba(0,196,159,0.35) !important;
        }

        [data-testid="stExpander"] summary {
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
        }

        /* ── INFO / ALERT BOXES ─────────────────────────────────────────── */

        [data-testid="stInfo"] {
            border-radius: 10px !important;
            border: 1px solid rgba(0,196,159,0.2) !important;
            background: rgba(0,196,159,0.04) !important;
            animation: fadeIn 0.4s ease-out;
        }

        [data-testid="stWarning"] {
            border-radius: 10px !important;
            animation: fadeIn 0.4s ease-out;
        }

        [data-testid="stSuccess"] {
            border-radius: 10px !important;
            animation: fadeIn 0.4s ease-out;
        }

        /* ── PROGRESS BARS ──────────────────────────────────────────────── */

        [data-testid="stProgress"] > div > div > div > div {
            background: linear-gradient(90deg, #00C49F 0%, #00A07F 100%) !important;
            border-radius: 4px !important;
            transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1) !important;
        }

        /* ── TABS ───────────────────────────────────────────────────────── */

        [data-testid="stTabs"] button[data-baseweb="tab"] {
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            transition: color 0.2s ease !important;
        }

        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #00C49F !important;
        }

        /* ── SIDEBAR ────────────────────────────────────────────────────── */

        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #0A0E16 0%, #0C1018 60%, #0E1117 100%) !important;
            border-right: 1px solid #1A2030 !important;
        }

        [data-testid="stSidebarNavLink"] {
            border-radius: 8px !important;
            transition: background 0.2s ease, padding-left 0.2s ease !important;
        }

        [data-testid="stSidebarNavLink"]:hover {
            background: rgba(0,196,159,0.08) !important;
            padding-left: 1.2rem !important;
        }

        /* ── DIVIDERS ───────────────────────────────────────────────────── */

        hr {
            border: none !important;
            border-top: 1px solid #1A2030 !important;
            opacity: 1 !important;
            margin: 1rem 0 !important;
        }

        /* ── CHARTS (Plotly) ────────────────────────────────────────────── */

        .js-plotly-plot {
            border-radius: 12px !important;
            animation: fadeIn 0.6s ease-out;
        }

        /* ── SCROLLBAR ──────────────────────────────────────────────────── */

        ::-webkit-scrollbar               { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track         { background: #0A0E16; }
        ::-webkit-scrollbar-thumb         { background: #252D3D; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover   { background: #00C49F; }

        /* ── PAGE LINKS (sidebar nav) ───────────────────────────────────── */

        [data-testid="stPageLink"] a {
            border-radius: 8px !important;
            transition: background 0.2s ease !important;
            padding: 0.3rem 0.6rem !important;
            display: block !important;
        }

        [data-testid="stPageLink"] a:hover {
            background: rgba(0,196,159,0.08) !important;
            text-decoration: none !important;
        }

        /* ── STAGGERED CARD ANIMATION HELPERS ───────────────────────────── */
        /* Apply these classes to HTML divs for sequential entrance */

        .wm-fade-1 { animation: fadeInUp 0.5s cubic-bezier(0.22,1,0.36,1) 0.05s both; }
        .wm-fade-2 { animation: fadeInUp 0.5s cubic-bezier(0.22,1,0.36,1) 0.15s both; }
        .wm-fade-3 { animation: fadeInUp 0.5s cubic-bezier(0.22,1,0.36,1) 0.25s both; }
        .wm-fade-4 { animation: fadeInUp 0.5s cubic-bezier(0.22,1,0.36,1) 0.35s both; }

        /* ── HERO TEAL GLOW BADGE ────────────────────────────────────────── */

        .wm-badge {
            display: inline-block;
            background: rgba(0,196,159,0.1);
            border: 1px solid rgba(0,196,159,0.3);
            border-radius: 20px;
            padding: 0.25rem 0.85rem;
            font-size: 0.78rem;
            font-weight: 500;
            color: #00C49F;
            letter-spacing: 0.04em;
            animation: fadeIn 0.6s ease-out 0.1s both;
        }

        /* ── HOVER CARD ─────────────────────────────────────────────────── */

        .wm-card {
            background: linear-gradient(145deg, #141B28 0%, #111620 100%);
            border: 1px solid #1E2738;
            border-radius: 12px;
            padding: 1.2rem;
            transition: transform 0.25s ease, border-color 0.25s ease,
                        box-shadow 0.25s ease;
            cursor: default;
        }

        .wm-card:hover {
            transform: translateY(-4px);
            border-color: rgba(0,196,159,0.4);
            box-shadow: 0 12px 35px rgba(0,196,159,0.1),
                        0 4px 12px rgba(0,0,0,0.4);
        }

        /* ── TEAL ACCENT LINE ───────────────────────────────────────────── */

        .wm-accent-left {
            border-left: 3px solid #00C49F;
            padding-left: 1rem;
        }

        /* ═══════════════════════════════════════════════════════════════════
           NAVIGATION PANEL — Premium redesign
           Styles Streamlit's sidebar into a Bloomberg / Linear-style nav.
           We deliberately keep the collapse button visible and do NOT
           override width or padding — that's what was hiding the sidebar.
        ═══════════════════════════════════════════════════════════════════ */

        /* ── Hide Streamlit's default top header bar ────────────────────── */

        header[data-testid="stHeader"] {
            display: none !important;
        }

        [data-testid="stDecoration"] {
            display: none !important;
        }

        /* ── Sidebar container — dark premium background only ────────────── */
        /* Do NOT override width, min-width, max-width, or padding —          */
        /* those overrides hide the sidebar or break the collapse toggle.      */

        [data-testid="stSidebar"] > div:first-child {
            background: #080D18 !important;
            border-right: 1px solid rgba(255,255,255,0.06) !important;
        }

        /* ── Page links → premium nav items ─────────────────────────────── */

        [data-testid="stPageLink"] {
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        [data-testid="stPageLink"] > div {
            padding: 0 !important;
            margin: 0 !important;
        }

        [data-testid="stPageLink"] a {
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
            padding: 0.54rem 1.25rem !important;
            border-radius: 0 !important;
            color: #56687A !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.875rem !important;
            font-weight: 400 !important;
            letter-spacing: 0.005em !important;
            text-decoration: none !important;
            transition: color 0.15s ease, background 0.15s ease,
                        border-left-color 0.15s ease !important;
            border-left: 2px solid transparent !important;
            border-right: 0 !important;
            border-top: 0 !important;
            border-bottom: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        [data-testid="stPageLink"] a:hover {
            color: #C4D0DB !important;
            background: rgba(255,255,255,0.04) !important;
            border-left-color: rgba(0,196,159,0.45) !important;
        }

        [data-testid="stPageLink"] a:active {
            background: rgba(255,255,255,0.06) !important;
        }

        /* Reset paragraph / span / div inside the anchor */
        [data-testid="stPageLink"] a p,
        [data-testid="stPageLink"] a span,
        [data-testid="stPageLink"] a div {
            color: inherit !important;
            font-size: inherit !important;
            font-family: inherit !important;
            font-weight: inherit !important;
            letter-spacing: inherit !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* ── Sidebar Sign-Out button ─────────────────────────────────────── */

        [data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.09) !important;
            color: #56687A !important;
            font-size: 0.8rem !important;
            font-weight: 400 !important;
            padding: 0.35rem 0.75rem !important;
            border-radius: 6px !important;
            transition: border-color 0.15s ease, color 0.15s ease,
                        background 0.15s ease !important;
            box-shadow: none !important;
            transform: none !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: rgba(239,68,68,0.35) !important;
            color: #F87171 !important;
            background: rgba(239,68,68,0.05) !important;
            transform: none !important;
            box-shadow: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
