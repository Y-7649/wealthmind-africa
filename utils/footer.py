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
                    padding:0.5rem 0 1rem 0;'>
            Created by
            <strong style='color:#555566;'>Yash Karia</strong>
            &nbsp;·&nbsp;
            <a href='mailto:yashkaria.pro@gmail.com'
               style='color:#444455; text-decoration:none;'>
                yashkaria.pro@gmail.com
            </a>
            &nbsp;·&nbsp;
            WealthMind Africa — Applying Economic Theory to Personal Financial Behaviour
        </div>
        """,
        unsafe_allow_html=True,
    )
