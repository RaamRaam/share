"""
config.py — Loads .env and exposes typed settings used across the system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_URL: str    = os.getenv("APP_URL", "")
SSO_EMAIL: str  = os.getenv("SSO_EMAIL", "").lower()

CHROME_USER_DATA_DIR = str(Path.home() / "Library/Application Support/Microsoft Edge")
CHROME_PROFILE = "Default"
BROWSER_ARGS   = [f"--profile-directory={CHROME_PROFILE}"]
HEADLESS       = os.getenv("HEADLESS", "false").lower() == "true"
SLOW_MO        = 150
