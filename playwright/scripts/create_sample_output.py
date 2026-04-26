"""
scripts/create_sample_output.py — Generate a sample output Excel file.

Produces output/sample_results.xlsx showing exactly what a real test run
report looks like — useful for sharing the expected format with stakeholders.

  python scripts/create_sample_output.py
"""

from datetime import datetime
from pathlib import Path
import sys

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from reporter import TestReporter

OUTPUT = "output/sample_results"

# ── Fabricated test data ───────────────────────────────────────────────────────

FAKE_RESULTS = [
    {
        "id": "TC001",
        "scenario": "Open app and verify home page",
        "module": "home",
        "status": "PASS",
        "error": "",
        "duration_s": 3.12,
        "steps": [
            {"step": 1, "description": "Navigate to the application URL",
             "function": "go_to",         "status": "PASS", "error": "", "duration_s": 1.84},
            {"step": 2, "description": "Assert URL loaded correctly",
             "function": "check_url",     "status": "PASS", "error": "", "duration_s": 0.11},
            {"step": 3, "description": "Assert page header is visible",
             "function": "check_visible", "status": "PASS", "error": "", "duration_s": 0.17},
        ],
    },
    {
        "id": "TC002",
        "scenario": "Login via SSO and land on dashboard",
        "module": "auth",
        "status": "PASS",
        "error": "",
        "duration_s": 12.47,
        "steps": [
            {"step": 1, "description": "Open application",
             "function": "go_to",         "status": "PASS", "error": "", "duration_s": 1.92},
            {"step": 2, "description": "Click the Sign In button",
             "function": "click",         "status": "PASS", "error": "", "duration_s": 0.34},
            {"step": 3, "description": "Wait for Microsoft login page",
             "function": "wait_for_url",  "status": "PASS", "error": "", "duration_s": 4.21},
            {"step": 4, "description": "Click SSO account tile",
             "function": "click",         "status": "PASS", "error": "", "duration_s": 0.55},
            {"step": 5, "description": "Wait for dashboard to load",
             "function": "wait_for_url",  "status": "PASS", "error": "", "duration_s": 5.45},
        ],
    },
    {
        "id": "TC003",
        "scenario": "Fill new-record form and submit",
        "module": "records",
        "status": "PASS",
        "error": "",
        "duration_s": 6.83,
        "steps": [
            {"step": 1, "description": "Open the New Record form",
             "function": "click",      "status": "PASS", "error": "", "duration_s": 0.41},
            {"step": 2, "description": "Fill Title field by placeholder",
             "function": "fill_input", "status": "PASS", "error": "", "duration_s": 0.28},
            {"step": 3, "description": "Fill Description field by label text",
             "function": "fill_input", "status": "PASS", "error": "", "duration_s": 0.31},
            {"step": 4, "description": "Fill Owner with SSO email from env",
             "function": "fill_input", "status": "PASS", "error": "", "duration_s": 0.29},
            {"step": 5, "description": "Submit form and assert redirect",
             "function": "click",      "status": "PASS", "error": "", "duration_s": 5.54},
        ],
    },
    {
        "id": "TC004",
        "scenario": "Search for a record and read its status",
        "module": "records",
        "status": "FAIL",
        "error": "Could not find adjacent text for label 'Status'",
        "duration_s": 4.09,
        "steps": [
            {"step": 1, "description": "Search for the new record",
             "function": "search_input",      "status": "PASS", "error": "", "duration_s": 1.77},
            {"step": 2, "description": "Read Status value next to its label",
             "function": "get_adjacent_text", "status": "FAIL",
             "error": "Could not find adjacent text for label 'Status'",
             "duration_s": 2.01},
            {"step": 3, "description": "Read Owner value next to its label",
             "function": "get_adjacent_text", "status": "FAIL",
             "error": "Skipped — previous step failed", "duration_s": 0.31},
        ],
    },
    {
        "id": "TC005",
        "scenario": "Edit a record via table action icon",
        "module": "records",
        "status": "PASS",
        "error": "",
        "duration_s": 5.22,
        "steps": [
            {"step": 1, "description": "Go to Records list page",
             "function": "click",         "status": "PASS", "error": "", "duration_s": 1.14},
            {"step": 2, "description": "Click the first icon (Edit) in the matching row",
             "function": "click_row_icon","status": "PASS", "error": "", "duration_s": 0.88},
            {"step": 3, "description": "Wait for edit page to load",
             "function": "wait_for_page", "status": "PASS", "error": "", "duration_s": 3.20},
        ],
    },
    {
        "id": "TC006",
        "scenario": "Delete a record via named icon in table",
        "module": "records",
        "status": "FAIL",
        "error": "No icon with name 'delete' in row containing 'Automation Test Record'",
        "duration_s": 2.15,
        "steps": [
            {"step": 1, "description": "Click the Delete icon by aria-label",
             "function": "click_row_icon", "status": "FAIL",
             "error": "No icon with name 'delete' in row containing 'Automation Test Record'",
             "duration_s": 2.15},
            {"step": 2, "description": "Confirm deletion in the dialog",
             "function": "click",          "status": "FAIL",
             "error": "Skipped — previous step failed", "duration_s": 0.0},
        ],
    },
    {
        "id": "TC007",
        "scenario": "Demo: sweep cursor to show automation",
        "module": "",
        "status": "PASS",
        "error": "",
        "duration_s": 3.05,
        "steps": [
            {"step": 1, "description": "Open the app",
             "function": "go_to",           "status": "PASS", "error": "", "duration_s": 1.04},
            {"step": 2, "description": "Sweep cursor across the page",
             "function": "demo_mouse_move", "status": "PASS", "error": "", "duration_s": 2.01},
        ],
    },
]


def main():
    r = TestReporter()
    # Inject pre-built results directly (bypasses live execution)
    now = datetime.now()
    for tc in FAKE_RESULTS:
        tc = dict(tc)
        tc["start"] = now.timestamp()
        r._results.append(tc)

    paths = r.to_files(OUTPUT)
    print(f"\n  Input sample  → tests/test_cases.xlsx")
    print(f"  Output sample → {paths[2].replace('_results.json', '_results.xlsx')}")


if __name__ == "__main__":
    main()
