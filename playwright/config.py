import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")
SSO_EMAIL = os.getenv("SSO_EMAIL").lower()

CHROME_USER_DATA_DIR = str(Path.home() / "Library/Application Support/Microsoft Edge")
CHROME_PROFILE = "Default"

BROWSER_ARGS = [f"--profile-directory={CHROME_PROFILE}"]
HEADLESS = False
SLOW_MO = 150
