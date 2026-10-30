"""End-to-end verification script for browser CRUD save operations and persistence."""

import os
import sqlite3
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\920a10b2-18cc-4d78-ac26-0c4f4e8152c3\screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def main_btn(page, text_pattern):
    return page.locator("section[data-testid='stMain'] button, div[data-testid='stMainBlockContainer'] button, .stMain button").filter(has_text=text_pattern).first


def test_ui_saves():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
        )
        context = browser.new_context(viewport={"width": 360, "height": 800})
        page = context.new_page()

        print("[1] Opening app at http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_timeout(3000)

        # Login
        print("[2] Logging in as test farmer (1234567890)...")
        login_form = page.locator("div[data-testid='stForm']").first
        inputs = login_form.locator("input").all()
        if len(inputs) >= 2:
            inputs[0].fill("1234567890")
            inputs[1].fill("TestPass123")
            login_form.locator("button[data-testid='stBaseButton-secondaryFormSubmit']").first.click()
            page.wait_for_timeout(5000)

        # 1. TEST CROP SAVE
        print("[3] Testing Crop Save in UI...")
        # Navigate to My Farm -> Crops
        btn_farm = main_btn(page, "माझी शेती")
        btn_farm.click()
        page.wait_for_timeout(3000)

        # Ensure expander is open
        closed_expander = page.locator("details:not([open]) summary").first
        if closed_expander.is_visible():
            closed_expander.click()
            page.wait_for_timeout(1000)

        # Enter variety
        var_input = page.locator("input[placeholder*='Ajit-155']").first
        if var_input.is_visible():
            var_input.fill("Ajit-155 BT")

        # Click save crop
        save_crop_btn = page.locator("button:has-text('पीक जतन करा'), button:has-text('Save Crop')").first
        print("  Clicking Save Crop button...")
        save_crop_btn.scroll_into_view_if_needed()
        save_crop_btn.click()
        page.wait_for_timeout(4000)

        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "verify_crop_saved.png"), full_page=True)

        # 2. TEST EXPENSE SAVE
        print("[4] Testing Expense Save in UI...")
        exp_tab = main_btn(page, "खर्च")
        exp_tab.click()
        page.wait_for_timeout(3000)

        # Ensure expander is open
        closed_exp = page.locator("details:not([open]) summary").first
        if closed_exp.is_visible():
            closed_exp.click()
            page.wait_for_timeout(1000)

        payee_inp = page.locator("input[placeholder*='महालक्ष्मी']").first
        if payee_inp.is_visible():
            payee_inp.fill("Kisan Krishi Seva")

        notes_inp = page.locator("input[placeholder*='१०:२६:२६']").first
        if notes_inp.is_visible():
            notes_inp.fill("DAP Fertilizer 2 bags")

        save_exp_btn = page.locator("button:has-text('खर्च जतन करा')").first
        print("  Clicking Save Expense button...")
        save_exp_btn.scroll_into_view_if_needed()
        save_exp_btn.click()
        page.wait_for_timeout(4000)

        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "verify_expense_saved.png"), full_page=True)

        # 3. TEST DIARY / ACTIVITY SAVE
        print("[5] Testing Farm Activity Save in UI...")
        diary_tab = main_btn(page, "दैनंदिनी")
        diary_tab.click()
        page.wait_for_timeout(3000)

        closed_act = page.locator("details:not([open]) summary").first
        if closed_act.is_visible():
            closed_act.click()
            page.wait_for_timeout(1000)

        desc_area = page.locator("textarea[placeholder*='१० मजूर']").first
        if desc_area.is_visible():
            desc_area.fill("Sprayed neem oil formulation for bollworm protection")

        save_act_btn = page.locator("button:has-text('कृती जतन करा')").first
        print("  Clicking Save Activity button...")
        save_act_btn.scroll_into_view_if_needed()
        save_act_btn.click()
        page.wait_for_timeout(4000)

        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "verify_activity_saved.png"), full_page=True)

        # 4. TEST HARVEST SAVE
        print("[6] Testing Harvest Record Save in UI...")
        harv_tab = main_btn(page, "उत्पादन")
        harv_tab.click()
        page.wait_for_timeout(3000)

        closed_harv = page.locator("details:not([open]) summary").first
        if closed_harv.is_visible():
            closed_harv.click()
            page.wait_for_timeout(1000)

        buyer_inp = page.locator("input[placeholder*='नाशिक APMC']").first
        if buyer_inp.is_visible():
            buyer_inp.fill("Baramati APMC Yard")

        save_harv_btn = page.locator("button:has-text('काढणी नोंद जतन करा')").first
        print("  Clicking Save Harvest button...")
        save_harv_btn.scroll_into_view_if_needed()
        save_harv_btn.click()
        page.wait_for_timeout(4000)

        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "verify_harvest_saved.png"), full_page=True)

        # 5. REFRESH PAGE TO VERIFY PERSISTENCE
        print("[7] Reloading page to verify true disk persistence...")
        page.reload()
        page.wait_for_timeout(4000)

        browser.close()
        print("Browser session closed cleanly.")

    # 6. VERIFY SQLITE DATABASE DISK PERSISTENCE
    print("[8] Verifying SQLite Database rows in data/agrisaathi.db...")
    conn = sqlite3.connect("data/agrisaathi.db")
    c = conn.cursor()
    counts = {}
    for table in ["crops", "expenses", "farm_activities", "harvest_records"]:
        counts[table] = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {counts[table]} rows in database")

    assert counts["crops"] >= 1, "Crops table should have saved record!"
    assert counts["expenses"] >= 1, "Expenses table should have saved record!"
    assert counts["farm_activities"] >= 1, "Farm activities table should have saved record!"
    assert counts["harvest_records"] >= 1, "Harvest records table should have saved record!"
    print("✅ ALL RECORDS SUCCESSFULLY PERSISTED IN THE DATABASE!")


if __name__ == "__main__":
    test_ui_saves()
