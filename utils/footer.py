"""
utils/footer.py
WealthMind Africa — Shared Footer

Defines render_footer() — called at the bottom of every page.
Subtle, professional, and consistent across the application.
"""

import streamlit as st


def render_footer():
    """
    Render the page footer with creator attribution.
    Intentionally understated — provides context without competing
    with the page content.
    """
    st.divider()
    st.markdown(
        """
        <div style='text-align:center; color:#444455; font-size:0.8rem;
                    padding:0.5rem 0 0.25rem 0;'>
            Created by
            <strong style='color:#555566;'>Yash Karia</strong>
            &nbsp;·&nbsp;
            <a href='mailto:wealthmind.insights@gmail.com'
               style='color:#444455; text-decoration:none;'>
                wealthmind.insights@gmail.com
            </a>
            &nbsp;·&nbsp;
            WealthMind Africa — Applying Economic Theory to Personal Financial Behaviour
        </div>
        <div style='text-align:center; color:#3A3A47; font-size:0.72rem;
                    letter-spacing:0.03em; padding:0 0 1rem 0;'>
            WealthMind Africa • Version 1.0 • July 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
