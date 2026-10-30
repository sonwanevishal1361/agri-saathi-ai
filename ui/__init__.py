"""AgriSaathi AI UI Package."""

from ui.state import init_session_state, get_current_farmer, set_current_farmer, logout
from ui.auth_pages import render_auth_page
from ui.dashboard import render_dashboard
from ui.crops_page import render_crops_page
from ui.crop_detail import render_crop_detail
from ui.knowledge_page import render_knowledge_page
from ui.chat_page import render_chat_page
from ui.diary_page import render_diary_page
from ui.expenses_page import render_expenses_page
from ui.harvest_page import render_harvest_page
from ui.weather_page import render_weather_page
from ui.market_page import render_market_page
from ui.schemes_page import render_schemes_page
from ui.image_page import render_image_page
from ui.profile_page import render_profile_page

__all__ = [
    "init_session_state",
    "get_current_farmer",
    "set_current_farmer",
    "logout",
    "render_auth_page",
    "render_dashboard",
    "render_crops_page",
    "render_crop_detail",
    "render_knowledge_page",
    "render_chat_page",
    "render_diary_page",
    "render_expenses_page",
    "render_harvest_page",
    "render_weather_page",
    "render_market_page",
    "render_schemes_page",
    "render_image_page",
    "render_profile_page",
]

