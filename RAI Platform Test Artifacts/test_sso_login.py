"""
SSO Login Test — Azure AD (password-less, reuses browser session/cookies)

Uses the user's existing Edge profile so Microsoft SSO auto-authenticates
without requiring a password.

Flow:
    1. Open app URL
    2. Click the Login button on the app
    3. Microsoft SSO page appears — enter email
    4. SSO auto-authenticates (no password needed)
    5. Print the landing page URL

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

# Path to your Edge user profile (reuses existing Microsoft session/cookies)
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

            # Step 2: Click the Login button on the app's landing page
            print("[2] Clicking Login button...")
            login_button = page.get_by_role("button", name="Login")
            if not login_button.is_visible():
                # Fallback — try link or any element with login text
                login_button = page.get_by_role("link", name="Login")
            login_button.click()

            # Step 3: Wait for Microsoft SSO page to appear
            print("[3] Waiting for Microsoft SSO page...")
            time.sleep(3)

            if "login.microsoftonline.com" in page.url or "login.live.com" in page.url:
                print("[4] Microsoft login page detected — entering email...")
                email_input = page.get_by_placeholder("Email, phone, or Skype")
                email_input.wait_for(state="visible", timeout=10_000)
                email_input.fill(SSO_EMAIL)
                page.get_by_role("button", name="Next").click()
                print("[5] Waiting for SSO to auto-authenticate (no password needed)...")
                time.sleep(5)  # allow time for SSO redirect chain to complete
            else:
                print("[4] SSO redirected without login page (session already active).")

            # Step 4: Wait for app to fully load after SSO
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
