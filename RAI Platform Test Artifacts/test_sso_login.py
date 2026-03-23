"""
SSO Login Test — Azure AD (password-less, reuses browser session/cookies)

Flow:
    1. Open app URL
    2. Click the Login button on the app
    3. Microsoft SSO account picker appears — click the pre-shown account
    4. App loads — print the landing page URL

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

            # Step 2: Click the Login button on the app
            print("[2] Clicking Login button...")
            login_button = page.locator("button:has-text('Login')")
            login_button.wait_for(state="visible", timeout=10_000)
            login_button.click()

            # Step 3: Wait for Microsoft SSO account picker
            print("[3] Waiting for Microsoft SSO account picker...")
            time.sleep(3)

            if "login.microsoftonline.com" in page.url:
                print(f"[4] Pick an account page detected — clicking {SSO_EMAIL}...")

                # Microsoft "Pick an account" page — try selectors in order
                selectors = [
                    f"[data-test-id='{SSO_EMAIL}']",           # standard tile attribute
                    f"[data-username='{SSO_EMAIL}']",           # alternative attribute
                    f"div.tile:has-text('{SSO_EMAIL}')",        # tile class with email text
                    f"div[role='option']:has-text('{SSO_EMAIL}')",  # ARIA option role
                    f"small:has-text('{SSO_EMAIL}')",           # email shown in <small>
                    f"p:has-text('{SSO_EMAIL}')",               # email shown in <p>
                ]

                account = None
                for selector in selectors:
                    loc = page.locator(selector)
                    if loc.count() > 0:
                        account = loc.first
                        print(f"    → matched with: {selector}")
                        break

                if account:
                    account.wait_for(state="visible", timeout=10_000)
                    account.click()
                else:
                    raise Exception(f"Could not find account tile for {SSO_EMAIL} on Pick an account page")

                print("[5] Waiting for app to load after SSO...")
                time.sleep(5)

            else:
                print("[4] SSO completed instantly (token silently reused).")
                time.sleep(3)

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
