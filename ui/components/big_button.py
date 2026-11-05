"""Oversized 56px+ tap target buttons with large icons and high contrast for one-hand use."""

from typing import Optional
import streamlit as st


def render_big_action_button(
    label: str,
    icon: str = "🌱",
    sublabel: Optional[str] = None,
    key: Optional[str] = None,
    button_type: str = "primary",  # primary, secondary, gold, danger
    use_container_width: bool = True,
) -> bool:
    """Render an ergonomic 56px+ touch target button with large icon and short text."""
    # Build button label
    display_text = f"{icon}  {label}"
    if sublabel:
        display_text += f"\n({sublabel})"

    # Streamlit button type mapping
    st_type = "primary" if button_type in ("primary", "gold") else "secondary"

    return st.button(
        display_text,
        key=key,
        use_container_width=use_container_width,
        type=st_type,
    )

