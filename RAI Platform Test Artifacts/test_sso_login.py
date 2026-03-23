"""
SSO Login Test — Azure AD (password-less, reuses browser session/cookies)

Uses the user's existing Chrome profile so Microsoft SSO auto-authenticates
without requiring a password.

Usage:
    pip install playwright python-dotenv
    playwright install chromium
    python test_sso_login.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

APP_URL = os.getenv("APP_URL")
SSO_EMAIL = os.getenv("SSO_EMAIL")
EXPECTED_HOME_URL = os.getenv("EXPECTED_HOME_URL")

# Path to your Chrome user profile (reuses existing Microsoft session/cookies)
CHROME_USER_DATA_DIR = str(Path.home() / "Library/Application Support/Google/Chrome")
CHROME_PROFILE = "Default"  # Change to "Profile 1", "Profile 2" etc. if needed


def test_sso_login() -> None:
    print(f"\n{'='*55}")
    print(f"  SSO Login Test")
    print(f"  App URL  : {APP_URL}")
    print(f"  Email    : {SSO_EMAIL}")
    print(f"{'='*55}")

    with sync_playwright() as p:
        # Launch with persistent Chrome profile so Microsoft session is reused
        context = p.chromium.launch_persistent_context(
            user_data_dir=CHROME_USER_DATA_DIR,
            channel="chrome",           # Use installed Chrome (not Chromium)
            args=[f"--profile-directory={CHROME_PROFILE}"],
            headless=False,             # Must be headed to reuse real profile
            slow_mo=500,
        )

        page = context.new_page()

        try:
            print("\n[1] Navigating to app...")
            page.goto(APP_URL, wait_until="networkidle", timeout=30_000)

            # If app redirects to Microsoft login, enter the email so it picks
            # up the correct tenant session, then wait for auto sign-in.
            if "login.microsoftonline.com" in page.url or "login.live.com" in page.url:
                print("[2] Microsoft login page detected — entering email...")

                email_input = page.get_by_placeholder("Email, phone, or Skype")
                email_input.wait_for(state="visible", timeout=10_000)
                email_input.fill(SSO_EMAIL)
                page.get_by_role("button", name="Next").click()

                print("[3] Waiting for SSO to auto-authenticate...")
                # Microsoft will use the existing browser session — no password needed
                page.wait_for_url(f"**{EXPECTED_HOME_URL.split('//')[1]}**", timeout=20_000)
            else:
                print("[2] Already authenticated — skipping Microsoft login page.")

            final_url = page.url
            success = EXPECTED_HOME_URL in final_url

            print(f"\n[Result] Final URL  : {final_url}")

            if success:
                print("[Result] SSO Login  : SUCCESS ✓")
                print(f"[Result] Landed on  : {final_url}")
            else:
                print("[Result] SSO Login  : FAILED ✗")
                print(f"[Result] Expected   : {EXPECTED_HOME_URL}")
                print(f"[Result] Got        : {final_url}")

        except Exception as e:
            print(f"\n[Result] SSO Login  : FAILED ✗")
            print(f"[Error]  {e}")
            success = False

        finally:
            context.close()

    print(f"{'='*55}\n")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    test_sso_login()
