"""Playwright script to capture mobile 360px APMC comparison screenshots in Marathi."""

import os
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\920a10b2-18cc-4d78-ac26-0c4f4e8152c3\screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def capture_mandi_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
        )
        context = browser.new_context(viewport={"width": 360, "height": 850})
        page = context.new_page()

        print("[1] Opening app at http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_timeout(3000)

        # Login
        print("[2] Logging in as test farmer (1234567890)...")
        login_form = page.locator("div[data-testid='stForm']").first
        if login_form.is_visible():
            inputs = login_form.locator("input").all()
            if len(inputs) >= 2:
                inputs[0].fill("1234567890")
                inputs[1].fill("TestPass123")
                login_form.locator("button[data-testid='stBaseButton-secondaryFormSubmit']").first.click()
                page.wait_for_timeout(4000)

        # Navigate to Market & Schemes
        print("[3] Navigating to Market & Schemes...")
        # Try finding button in main container or navigation
        market_btn = page.locator("button:has-text('बाजार व योजना'), button:has-text('Market & Schemes'), button:has-text('दर पहा')").first
        if market_btn.is_visible():
            market_btn.click()
            page.wait_for_timeout(3000)

        # Confirm we are on market page
        page.wait_for_selector("h1:has-text('बाजारभाव'), h1:has-text('APMC')", timeout=10000)
        print("Market page loaded successfully!")

        # 1. COTTON SCREENSHOT (कापूस)
        print("[4] Capturing Cotton APMC comparison...")
        cotton_path = os.path.join(SCREENSHOTS_DIR, "mandi_comparison_cotton_mr_360.png")
        page.screenshot(path=cotton_path, full_page=False)
        print(f"Saved: {cotton_path}")

        # Scroll to show top markets comparison chart & distance
        page.evaluate("window.scrollBy(0, 500)")
        page.wait_for_timeout(1000)
        cotton_details_path = os.path.join(SCREENSHOTS_DIR, "mandi_comparison_cotton_details_mr_360.png")
        page.screenshot(path=cotton_details_path, full_page=False)
        print(f"Saved: {cotton_details_path}")

        # 2. SOYBEAN SCREENSHOT (सोयाबीन)
        print("[5] Selecting Soybean...")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        # Open commodity selectbox
        comm_select = page.locator("div[data-testid='stSelectbox']").filter(has_text="शेतमाल").first
        if not comm_select.is_visible():
            comm_select = page.locator("div[data-testid='stSelectbox']").first
        comm_select.click()
        page.wait_for_timeout(800)

        # Select Soybean
        soy_option = page.locator("li[role='option']:has-text('Soybean')").first
        if soy_option.is_visible():
            soy_option.click()
            page.wait_for_timeout(3000)

        soy_path = os.path.join(SCREENSHOTS_DIR, "mandi_comparison_soybean_mr_360.png")
        page.screenshot(path=soy_path, full_page=False)
        print(f"Saved: {soy_path}")

        # Scroll to show WhatsApp sharing and profit calculator
        page.evaluate("window.scrollBy(0, 800)")
        page.wait_for_timeout(1000)
        soy_tools_path = os.path.join(SCREENSHOTS_DIR, "mandi_comparison_soybean_tools_mr_360.png")
        page.screenshot(path=soy_tools_path, full_page=False)
        print(f"Saved: {soy_tools_path}")

        browser.close()
        print("Done capturing all screenshots!")


if __name__ == "__main__":
    capture_mandi_screenshots()
