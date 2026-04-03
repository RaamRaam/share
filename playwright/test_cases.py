"""
test_cases.py — One function per test case.

Pattern
───────
Each test-case function:
  1. Calls reporter.start_test(tc_num, scenario_description)
  2. Defines `steps` — an ordered list of (description, lambda) tuples
  3. Calls reporter.run_steps(steps) which executes each step,
     logs PASS / FAIL per step, calls end_test(), and returns True / False.

Adding a new test case
──────────────────────
  • Copy any existing tc_XXX function.
  • Update the TC number, scenario, and steps list.
  • Append the function to TEST_CASES at the bottom — execution order follows list order.
"""

from config import APP_URL, SSO_EMAIL
from actions import (
    navigate,
    click_button,
    click_button_ci,
    click_by_selector,
    check_url,
    check_title,
    wait_for_url,
    populate_textbox,
    clear_textbox,
    choose_dropdown,
    choose_react_dropdown,
    multi_select_dropdown,
    extract_div_content,
    get_element_attribute,
    check_value_in_div,
    check_element_visible,
    check_element_count,
    wait_for_element,
    wait_for_load,
)
from page_actions import (
    click_comprehensive_risk_assessment,
    click_run_qualitative_assessment,
    select_os_summary,
    click_assessment_icon,
    answer_all_questions,
    click_save,
)


# ─────────────────────────────────────────────────────────────────────────────
# TC-001 : Open application & verify home page
# ─────────────────────────────────────────────────────────────────────────────
def tc_001_open_app(page, reporter):
    reporter.start_test("TC-001", "Open application and verify home page loads")

    steps = [
        ("Navigate to APP_URL",
         lambda: navigate(page, APP_URL)),

        ("Verify current URL contains APP_URL",
         lambda: check_url(page, APP_URL)),

        ("Verify page header / hero element is visible",
         lambda: check_element_visible(page, "header, h1, [data-testid='app-header']")),

        ("Wait for network idle after load",
         lambda: wait_for_load(page)),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-002 : Login via Microsoft SSO
# ─────────────────────────────────────────────────────────────────────────────
def tc_002_login(page, reporter):
    reporter.start_test("TC-002", "Login via Microsoft SSO")

    steps = [
        ("Click Login / Sign In button (case-insensitive)",
         lambda: click_button_ci(page, ["login", "sign in"])),

        ("Wait for redirect to Microsoft login page",
         lambda: wait_for_url(page, "**login.microsoftonline.com**", timeout=15_000)),

        ("Verify Microsoft login page URL",
         lambda: check_url(page, "microsoftonline.com")),

        (f"Click SSO account tile for {SSO_EMAIL}",
         lambda: click_by_selector(page, f"[data-test-id='{SSO_EMAIL}']")),

        ("Wait for redirect back to app home",
         lambda: wait_for_url(page, "**/home**", timeout=20_000)),

        ("Verify app home URL after login",
         lambda: check_url(page, "/home")),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-003 : Navigate to Comprehensive Risk Assessment
# ─────────────────────────────────────────────────────────────────────────────
def tc_003_navigate_to_risk_assessment(page, reporter):
    reporter.start_test("TC-003", "Navigate to Comprehensive Risk Assessment")

    steps = [
        ("Click Comprehensive Risk Assessment link",
         lambda: click_comprehensive_risk_assessment(page)),

        ("Verify URL contains 'risk' or 'assessment'",
         lambda: check_url(page, "assessment")),

        ("Verify page heading is visible",
         lambda: check_element_visible(page, "h1, h2, [data-testid='page-title']")),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-004 : Select Qualitative Assessment card
# ─────────────────────────────────────────────────────────────────────────────
def tc_004_select_qualitative_assessment(page, reporter):
    reporter.start_test("TC-004", "Select Run Qualitative Assessment card")

    steps = [
        ("Click Run Qualitative Assessment card",
         lambda: click_run_qualitative_assessment(page)),

        ("Verify at least one card container is visible",
         lambda: check_element_visible(page, 'div[class*="cardContainer"]')),

        ("Wait for page to settle",
         lambda: wait_for_load(page)),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-005 : Select OS Summary from dropdown
# ─────────────────────────────────────────────────────────────────────────────
def tc_005_select_os_summary(page, reporter):
    reporter.start_test("TC-005", "Select OS Summary from react-select dropdown")

    steps = [
        ("Verify react-select control is present",
         lambda: check_element_visible(page, "div.react-select__control")),

        ("Open dropdown and choose OS-SUMMARY option",
         lambda: select_os_summary(page)),

        ("Verify selected value contains 'OS' or 'Summary'",
         lambda: check_value_in_div(page, "div.react-select__single-value", "Summary")),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-006 : Click Assessment icon to open questionnaire
# ─────────────────────────────────────────────────────────────────────────────
def tc_006_click_assessment_icon(page, reporter):
    reporter.start_test("TC-006", "Click Assessment icon to open questionnaire")

    steps = [
        ("Verify Assessment icon is visible",
         lambda: check_element_visible(page, '[aria-label="Assessment"]')),

        ("Click Assessment icon",
         lambda: click_assessment_icon(page)),

        ("Wait for questionnaire panel to load",
         lambda: wait_for_load(page)),

        ("Verify at least one accordion item is present",
         lambda: wait_for_element(page, ".accordionItem, [data-testid='parent-question']",
                                  timeout=10_000)),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-007 : Answer all questionnaire items
# ─────────────────────────────────────────────────────────────────────────────
def tc_007_answer_all_questions(page, reporter):
    reporter.start_test("TC-007", "Answer all questionnaire items (Yes/No + text fields)")

    steps = [
        ("Verify accordion questions are visible",
         lambda: check_element_visible(page, ".accordionItem")),

        ("Count visible parent questions (expect > 0)",
         lambda: _assert_positive(page.locator(".accordionItem").count(),
                                  "No parent accordion items found")),

        ("Expand all sections and answer every sub-question",
         lambda: answer_all_questions(page)),

        ("Verify no unanswered Yes/No groups remain",
         lambda: _assert_no_unanswered(page)),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-008 : Save the completed assessment
# ─────────────────────────────────────────────────────────────────────────────
def tc_008_save_assessment(page, reporter):
    reporter.start_test("TC-008", "Save the completed assessment")

    steps = [
        ("Click Save button",
         lambda: click_save(page)),

        ("Wait for save confirmation / network idle",
         lambda: wait_for_load(page)),

        ("Verify success toast / confirmation element is visible",
         lambda: wait_for_element(page,
                                  "[data-testid='toast-success'], .success-banner, "
                                  "[aria-label='success'], .notification-success",
                                  timeout=8_000)),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-009 : Demo — dropdown, textbox, multi-select, div content checks
#          (replace selectors with real ones from your app)
# ─────────────────────────────────────────────────────────────────────────────
def tc_009_form_interactions_demo(page, reporter):
    reporter.start_test(
        "TC-009",
        "Form interactions: textbox, native dropdown, multi-select, div content checks"
    )

    steps = [
        # ── textbox ──
        ("Populate search / filter text box",
         lambda: populate_textbox(page, "input[placeholder*='Search'], input[type='text']",
                                  "Test Input", nth=0)),

        ("Verify text box value is set",
         lambda: _assert_input_value(page,
                                     "input[placeholder*='Search'], input[type='text']",
                                     "Test Input")),

        ("Clear the text box",
         lambda: clear_textbox(page, "input[placeholder*='Search'], input[type='text']")),

        # ── native <select> dropdown ──
        ("Choose option from native dropdown (if present)",
         lambda: choose_dropdown(page, "select", "Option 1")),

        # ── react-select single ──
        ("Choose item from react-select dropdown",
         lambda: choose_react_dropdown(page, "div.react-select", "OS-SUMMARY")),

        # ── react-select multi ──
        ("Multi-select two items from react-select",
         lambda: multi_select_dropdown(page, "div.react-select--multi",
                                       ["Option A", "Option B"])),

        # ── div content extraction & assertion ──
        ("Extract content from result div",
         lambda: extract_div_content(page, "div[data-testid='result-panel']")),

        ("Assert result div contains expected text",
         lambda: check_value_in_div(page, "div[data-testid='result-panel']",
                                    "Saved", contains=True)),

        ("Read an element attribute (e.g. aria-label)",
         lambda: get_element_attribute(page, "[data-testid='status-badge']", "aria-label")),

        ("Verify element count matches expectation",
         lambda: check_element_count(page, ".accordionItem", 5)),
    ]

    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# Private assertion helpers (keep small; don't repeat complex logic here)
# ─────────────────────────────────────────────────────────────────────────────

def _assert_positive(value: int, msg: str) -> bool:
    assert value > 0, msg
    return True


def _assert_no_unanswered(page) -> bool:
    """Check that no Yes/No group has all radio buttons unchecked."""
    groups = page.locator(".yesNoGroup").all()
    unanswered = 0
    for g in groups:
        checked = g.locator("input[type='radio']:checked").count()
        if checked == 0:
            unanswered += 1
    assert unanswered == 0, f"{unanswered} unanswered Yes/No group(s) remain"
    return True


def _assert_input_value(page, selector: str, expected: str) -> bool:
    actual = page.locator(selector).first.input_value()
    assert actual == expected, f"Input value mismatch: expected '{expected}', got '{actual}'"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Execution order — append new TCs here
# ─────────────────────────────────────────────────────────────────────────────

TEST_CASES = [
    tc_001_open_app,
    tc_002_login,
    tc_003_navigate_to_risk_assessment,
    tc_004_select_qualitative_assessment,
    tc_005_select_os_summary,
    tc_006_click_assessment_icon,
    tc_007_answer_all_questions,
    tc_008_save_assessment,
    # tc_009_form_interactions_demo,   # ← enable when selectors are confirmed
]
