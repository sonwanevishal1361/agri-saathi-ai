"""Playwright mobile browser walkthrough (360px viewport) across all pages and languages."""

import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\920a10b2-18cc-4d78-ac26-0c4f4e8152c3\screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def check_for_errors(page, page_name):
    """Check if any error alerts or exceptions are rendered on the page."""
    errors = page.locator("div[data-testid='stAlert']").all()
    found_errors = []
    for alert in errors:
        txt = alert.inner_text().strip()
        # Streamlit error alerts usually contain error keywords or specific styles
        if "error" in txt.lower() or "exception" in txt.lower() or "traceback" in txt.lower() or "❌" in txt:
            found_errors.append(txt)
    if found_errors:
        print(f"⚠️ ERRORS DETECTED ON [{page_name}]: {found_errors}")
    else:
        print(f"✅ [{page_name}] loaded cleanly without errors.")
    return found_errors


def main_btn(page, text_pattern):
    """Find a button with given text strictly inside the main content area (not sidebar)."""
    return page.locator("section[data-testid='stMain'] button, div[data-testid='stMainBlockContainer'] button").filter(has_text=text_pattern).first


def run_walkthrough():
    all_page_errors = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
        )
        context = browser.new_context(viewport={"width": 360, "height": 800})
        page = context.new_page()

        print("[1] Opening app at 360px...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_timeout(3000)

        # 1. Login page screenshot (Marathi)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01_login_mr_360.png"), full_page=True)
        print("Captured: 01_login_mr_360.png")
        all_page_errors["login_mr"] = check_for_errors(page, "Login (Marathi)")

        # Login
        print("[2] Logging in as test farmer...")
        login_form = page.locator("div[data-testid='stForm']").first
        inputs = login_form.locator("input").all()
        if len(inputs) >= 2:
            inputs[0].fill("1234567890")
            inputs[1].fill("TestPass123")
            submit_btn = login_form.locator("button[data-testid='stBaseButton-secondaryFormSubmit']").first
            submit_btn.click()
            page.wait_for_timeout(4000)

        # 2. Dashboard screenshot (Home)
        print("[3] Capturing Home Dashboard...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02_dashboard_home_mr_360.png"), full_page=True)
        print("Captured: 02_dashboard_home_mr_360.png")
        all_page_errors["dashboard"] = check_for_errors(page, "Home Dashboard")

        # 3. Navigation to Ask AI
        print("[4] Navigating to Ask AI...")
        btn_chat = main_btn(page, "AI सल्ला")
        if btn_chat.is_visible():
            btn_chat.click()
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "03_chat_ai_360.png"), full_page=True)
            print("Captured: 03_chat_ai_360.png")
            all_page_errors["chat"] = check_for_errors(page, "Ask AI")

        # 4. Navigation to My Farm
        print("[5] Navigating to My Farm...")
        btn_farm = main_btn(page, "माझी शेती")
        if btn_farm.is_visible():
            btn_farm.click()
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "04_my_farm_crops_360.png"), full_page=True)
            print("Captured: 04_my_farm_crops_360.png")
            all_page_errors["farm_crops"] = check_for_errors(page, "My Farm: Crops")

            # Click Diary subtab
            diary_sub = main_btn(page, "दैनंदिनी")
            if diary_sub.is_visible():
                diary_sub.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "05_farm_diary_360.png"), full_page=True)
                print("Captured: 05_farm_diary_360.png")
                all_page_errors["farm_diary"] = check_for_errors(page, "My Farm: Diary")

            # Click Expenses subtab
            exp_sub = main_btn(page, "खर्च")
            if exp_sub.is_visible():
                exp_sub.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "06_farm_expenses_360.png"), full_page=True)
                print("Captured: 06_farm_expenses_360.png")
                all_page_errors["farm_expenses"] = check_for_errors(page, "My Farm: Expenses")

            # Click Harvest subtab
            harv_sub = main_btn(page, "उत्पादन")
            if harv_sub.is_visible():
                harv_sub.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "07_farm_harvest_360.png"), full_page=True)
                print("Captured: 07_farm_harvest_360.png")
                all_page_errors["farm_harvest"] = check_for_errors(page, "My Farm: Harvest")

        # 5. Navigation to Market & Schemes
        print("[6] Navigating to Market & Schemes...")
        market_btn = main_btn(page, "बाजार व योजना")
        if market_btn.is_visible():
            market_btn.click()
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "08_market_mandi_360.png"), full_page=True)
            print("Captured: 08_market_mandi_360.png")
            all_page_errors["market_mandi"] = check_for_errors(page, "Market: Mandi Prices")

            # Weather subtab
            weath_sub = main_btn(page, "हवामान")
            if weath_sub.is_visible():
                weath_sub.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "09_market_weather_360.png"), full_page=True)
                print("Captured: 09_market_weather_360.png")
                all_page_errors["market_weather"] = check_for_errors(page, "Market: Weather")

            # Schemes subtab
            sch_sub = main_btn(page, "योजना")
            if sch_sub.is_visible():
                sch_sub.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "10_market_schemes_360.png"), full_page=True)
                print("Captured: 10_market_schemes_360.png")
                all_page_errors["market_schemes"] = check_for_errors(page, "Market: Schemes")

            # Leaf disease check subtab
            img_sub = main_btn(page, "रोग तपासणी")
            if img_sub.is_visible():
                img_sub.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "11_crop_health_360.png"), full_page=True)
                print("Captured: 11_crop_health_360.png")
                all_page_errors["crop_health"] = check_for_errors(page, "Market: Leaf Health")

        # 6. Navigation to Profile
        print("[7] Navigating to Profile...")
        prof_btn = main_btn(page, "माझे खाते")
        if prof_btn.is_visible():
            prof_btn.click()
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "12_profile_360.png"), full_page=True)
            print("Captured: 12_profile_360.png")
            all_page_errors["profile"] = check_for_errors(page, "Farmer Profile")

        browser.close()
        print("\n=== WALKTHROUGH COMPLETE ===")
        print(f"Total pages checked: {len(all_page_errors)}")
        error_count = sum(len(errs) for errs in all_page_errors.values())
        print(f"Total UI errors detected: {error_count}")
        return all_page_errors


if __name__ == "__main__":
    run_walkthrough()
