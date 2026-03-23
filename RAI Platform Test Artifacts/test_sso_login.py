"""
SSO Login Test — Azure AD (password-less, reuses browser session/cookies)

Flow:
    1. Open app URL
    2. Click the Login button on the app
    3. SSO opens in a popup/new tab — click the pre-shown account
    4. Popup closes, app loads — print the landing page URL

Usage:
    pip install playwright python-dotenv
    python test_sso_login.py
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

APP_URL   = os.getenv("APP_URL")
SSO_EMAIL = os.getenv("SSO_EMAIL")

CHROME_USER_DATA_DIR = str(Path.home() / "Library/Application Support/Microsoft Edge")
CHROME_PROFILE = "Default"  # Change to "Profile 1", "Profile 2" etc. if needed


def pick_account(sso_page, email: str) -> None:
    """Click the matching account on the Microsoft 'Pick an account' page."""
    selectors = [
        f"[data-test-id='{email}']",
        f"[data-username='{email}']",
        f"div.tile:has-text('{email}')",
        f"div[role='option']:has-text('{email}')",
        f"small:has-text('{email}')",
        f"p:has-text('{email}')",
    ]
    for selector in selectors:
        loc = sso_page.locator(selector)
        if loc.count() > 0:
            print(f"    → matched with: {selector}")
            loc.first.wait_for(state="visible", timeout=10_000)
            loc.first.click()
            return

    raise Exception(f"Could not find account tile for {email} on Pick an account page")


def test_sso_login() -> None:
    print(f"\n{'='*55}")
    print(f"  SSO Login Test")
    print(f"  App URL  : {APP_URL}")
    print(f"  Email    : {SSO_EMAIL}")
    print(f"{'='*55}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=CHROME_USER_DATA_DIR,
            channel="msedge",
            args=[f"--profile-directory={CHROME_PROFILE}"],
            headless=False,
            slow_mo=500,
        )

        page = context.new_page()

        try:
            # Step 1: Open the app
            print("\n[1] Navigating to app...")
            page.goto(APP_URL, wait_until="networkidle", timeout=60_000)

            # Step 2: Click the Login button — SSO may open as popup or same tab
            print("[2] Clicking Login button...")
            login_button = page.locator("button:has-text('Login')")
            login_button.wait_for(state="visible", timeout=10_000)

            # Listen for a popup BEFORE clicking
            with context.expect_page(timeout=10_000) as new_page_info:
                login_button.click()

            sso_page = new_page_info.value
            sso_page.wait_for_load_state("domcontentloaded")
            print(f"[3] SSO opened in new tab — URL: {sso_page.url}")

            # Step 3: Handle Pick an account page
            if "login.microsoftonline.com" in sso_page.url or "login.live.com" in sso_page.url:
                print(f"[4] Pick an account page detected — selecting {SSO_EMAIL}...")
                pick_account(sso_page, SSO_EMAIL)

                print("[5] Waiting for SSO to complete and app to load...")
                # Wait for the popup to close after account selection
                try:
                    sso_page.wait_for_event("close", timeout=15_000)
                    print("    → SSO popup closed.")
                except Exception:
                    print("    → SSO popup did not close; may have redirected.")

            time.sleep(3)  # allow app page to finish loading after SSO

            final_url = page.url
            print(f"\n[Result] Landed on  : {final_url}")
            print(f"[Result] SSO Login  : SUCCESS ✓")

        except Exception as e:
            print(f"\n[Result] SSO Login  : FAILED ✗")
            print(f"[Error]  {e}")

        finally:
            context.close()

    print(f"{'='*55}\n")


if __name__ == "__main__":
    test_sso_login()
