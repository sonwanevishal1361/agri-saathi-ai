"""Shimmering loading placeholder skeletons for cards and metrics."""

import textwrap
import streamlit as st


def render_skeleton_card(height: int = 120, count: int = 1):
    """Render shimmering skeleton placeholder boxes."""
    html = ""
    for _ in range(count):
        html += f'<div class="skeleton-box" style="height: {height}px;"></div>'
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)

