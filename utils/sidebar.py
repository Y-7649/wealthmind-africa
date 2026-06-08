"""
utils/sidebar.py
WealthMind Africa — Premium Navigation Panel

render_sidebar(current_page) builds the full navigation panel and injects
the global CSS design system.  Call it near the top of every authenticated
page.

The current_page parameter controls which nav item is shown as active
(highlighted with the teal accent).  Valid identifiers:

    "kenya_context" Kenya Economic Context (public)
    "home"          Home / overview dashboard
    "dashboard"     Transaction ledger
    "health_score"  Financial Health Score
    "inflation"     Kenya Inflation Context
    "projection"    Wealth Projection
    "behaviour"     Behavioural Analysis
    "about"         About the Creator
    ""              No item highlighted (default)
"""

import streamlit as st
from utils.styles import inject_global_styles


# ── NAV HELPER FUNCTIONS ──────────────────────────────────────────────────────

def _active_item(label: str) -> str:
    """
    Return the HTML for an active (current page) nav item.
    Uses the same padding and font as the CSS-styled st.page_link() so
    both item types look visually consistent when stacked together.
    """
    return (
        '<div style="'
        'display:flex;align-items:center;'
        'padding:0.54rem 1.25rem;'
        'color:#00C49F;'
        'background:rgba(0,196,159,0.09);'
        'border-left:2px solid #00C49F;'
        'font-family:Inter,sans-serif;'
        'font-size:0.875rem;font-weight:500;'
        'letter-spacing:0.005em;'
        'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
        'cursor:default;user-select:none;">'
        f'{label}'
        '</div>'
    )


def _section_label(text: str) -> str:
    """Return HTML for a nav section heading (very subtle ghost text)."""
    return (
        '<div style="'
        'font-family:Inter,sans-serif;font-size:0.65rem;font-weight:600;'
        'color:#4A6070;letter-spacing:0.12em;text-transform:uppercase;'
        'padding:0.9rem 1.25rem 0.3rem;">'
        f'{text}'
        '</div>'
    )


# ── MAIN FUNCTION ─────────────────────────────────────────────────────────────

def render_sidebar(current_page: str = ""):
    """
    Render the premium navigation panel and inject the global design system.

    Parameters
    ----------
    current_page : str
        Identifier for the page that should appear active in the nav.
        See module docstring for valid values.
    """
    inject_global_styles()

    with st.sidebar:

        # ── BRAND HEADER ──────────────────────────────────────────────────────

        st.markdown(
            '<div style="'
            'padding:1.4rem 1.2rem 1.1rem;'
            'border-bottom:1px solid rgba(255,255,255,0.07);'
            'margin-bottom:0.15rem;">'

            '<div style="display:flex;align-items:center;gap:0.65rem;">'
            '<span style="font-size:1.3rem;line-height:1;flex-shrink:0;">🌍</span>'
            '<div>'
            '<div style="'
            'font-family:Inter,sans-serif;font-size:0.88rem;font-weight:700;'
            'color:#E2E8F0;letter-spacing:-0.015em;line-height:1.2;">'
            'WealthMind Africa'
            '</div>'
            '<div style="'
            'font-family:Inter,sans-serif;font-size:0.64rem;color:#4A6070;'
            'letter-spacing:0.07em;text-transform:uppercase;margin-top:0.15rem;">'
            'Applied Economics'
            '</div>'
            '</div>'
            '</div>'

            '</div>',
            unsafe_allow_html=True,
        )

        # ── EXPLORE (public) ──────────────────────────────────────────────────

        st.markdown(_section_label("Explore"), unsafe_allow_html=True)

        if current_page == "kenya_context":
            st.markdown(_active_item("🌍  Kenya Economic Context"), unsafe_allow_html=True)
        else:
            st.page_link("pages/0_kenya_context.py", label="🌍  Kenya Economic Context")

        # ── PLATFORM ─────────────────────────────────────────────────────────

        st.markdown(_section_label("Platform"), unsafe_allow_html=True)

        if current_page == "home":
            st.markdown(_active_item("🏠  Home"), unsafe_allow_html=True)
        else:
            st.page_link("app.py", label="🏠  Home")

        if current_page == "dashboard":
            st.markdown(_active_item("💳  Dashboard"), unsafe_allow_html=True)
        else:
            st.page_link("pages/1_dashboard.py", label="💳  Dashboard")

        # ── ANALYSIS ─────────────────────────────────────────────────────────

        st.markdown(_section_label("Analysis"), unsafe_allow_html=True)

        if current_page == "health_score":
            st.markdown(_active_item("📊  Financial Health Score"), unsafe_allow_html=True)
        else:
            st.page_link("pages/2_health_score.py", label="📊  Financial Health Score")

        if current_page == "inflation":
            st.markdown(_active_item("🇰🇪  Kenya Inflation Context"), unsafe_allow_html=True)
        else:
            st.page_link("pages/3_inflation.py", label="🇰🇪  Kenya Inflation Context")

        if current_page == "projection":
            st.markdown(_active_item("📈  Wealth Projection"), unsafe_allow_html=True)
        else:
            st.page_link("pages/4_projection.py", label="📈  Wealth Projection")

        if current_page == "behaviour":
            st.markdown(_active_item("🧠  Behavioural Analysis"), unsafe_allow_html=True)
        else:
            st.page_link("pages/5_behaviour.py", label="🧠  Behavioural Analysis")

        # ── INFO ──────────────────────────────────────────────────────────────

        st.markdown(_section_label("Info"), unsafe_allow_html=True)

        if current_page == "about":
            st.markdown(_active_item("👨‍💻  About the Creator"), unsafe_allow_html=True)
        else:
            st.page_link("pages/6_about.py", label="👨‍💻  About the Creator")

        # ── LOGGED-IN USER & SIGN OUT ─────────────────────────────────────────

        if st.session_state.get("logged_in") and st.session_state.get("user"):
            user = st.session_state.user

            st.markdown(
                '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);'
                'margin:0.8rem 0 0 0;">',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div style="padding:0.55rem 1.25rem;">'
                f'<div style="font-family:Inter,sans-serif;font-size:0.8rem;'
                f'font-weight:500;color:#7A8EA0;">👤 {user["username"]}</div>'
                f'<div style="font-family:Inter,sans-serif;font-size:0.69rem;'
                f'color:#4A6070;margin-top:0.1rem;">'
                f'member since {user["created_at"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            sign_out_col, _ = st.columns([3, 1])
            with sign_out_col:
                if st.button("Sign Out", use_container_width=True, key="nav_sign_out"):
                    st.session_state.logged_in = False
                    st.session_state.user      = None
                    st.rerun()

        # ── CREATOR FOOTER ────────────────────────────────────────────────────

        st.markdown(
            '<div style="'
            'padding:0.9rem 1.25rem 1rem;'
            'border-top:1px solid rgba(255,255,255,0.07);'
            'margin-top:1.2rem;">'

            '<div style="'
            'font-family:Inter,sans-serif;font-size:0.78rem;'
            'font-weight:600;color:#7A8EA0;">'
            'Yash Karia'
            '</div>'

            '<div style="'
            'font-family:Inter,sans-serif;font-size:0.7rem;'
            'color:#4A6070;margin-top:0.1rem;">'
            '<a href="mailto:yashkaria.pro@gmail.com" '
            'style="color:inherit;text-decoration:none;">'
            'yashkaria.pro@gmail.com'
            '</a>'
            '</div>'

            '</div>',
            unsafe_allow_html=True,
        )
