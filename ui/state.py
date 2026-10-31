"""Session state management helpers for AgriSaathi AI."""

import streamlit as st
from typing import Optional
from core.auth import AuthenticatedFarmer

PAGE_TO_SECTION = {
    "dashboard": "home",
    "chat": "chat",
    "crops": "my_farm",
    "crop_detail": "my_farm",
    "diary": "my_farm",
    "expenses": "my_farm",
    "harvest": "my_farm",
    "market": "market_schemes",
    "weather": "market_schemes",
    "schemes": "market_schemes",
    "knowledge": "market_schemes",
    "image": "market_schemes",
    "profile": "profile",
    "admin": "admin",
}


def init_session_state():
    """Initialize default session state keys if not set."""
    if "farmer" not in st.session_state:
        st.session_state["farmer"] = None
    if "language" not in st.session_state:
        st.session_state["language"] = "mr"  # Default Marathi
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"
    if "active_section" not in st.session_state:
        st.session_state["active_section"] = "home"
    if "selected_crop_id" not in st.session_state:
        st.session_state["selected_crop_id"] = None
    if "active_conversation_id" not in st.session_state:
        st.session_state["active_conversation_id"] = None
    if "chat_crop_filter" not in st.session_state:
        st.session_state["chat_crop_filter"] = None


def get_current_farmer() -> Optional[AuthenticatedFarmer]:
    """Return currently logged-in farmer session object."""
    return st.session_state.get("farmer")


def set_current_farmer(farmer: Optional[AuthenticatedFarmer]):
    """Set authenticated farmer session object and initialize language preference."""
    st.session_state["farmer"] = farmer
    if farmer and farmer.preferred_language:
        st.session_state["language"] = farmer.preferred_language


def logout():
    """Clear session and log out the user."""
    st.session_state["farmer"] = None
    st.session_state["selected_crop_id"] = None
    st.session_state["active_conversation_id"] = None
    st.session_state["current_page"] = "dashboard"
    st.session_state["active_section"] = "home"


def get_language() -> str:
    """Return current UI language code (en, mr, hi)."""
    return st.session_state.get("language", "mr")


def set_language(lang: str):
    """Set current UI language code."""
    st.session_state["language"] = lang
    farmer = st.session_state.get("farmer")
    if farmer:
        farmer.preferred_language = lang


def set_page(page_name: str, crop_id: Optional[str] = None):
    """Navigate to another page and keep section in sync."""
    st.session_state["current_page"] = page_name
    st.session_state["active_section"] = PAGE_TO_SECTION.get(page_name, "home")
    if crop_id is not None:
        st.session_state["selected_crop_id"] = crop_id
