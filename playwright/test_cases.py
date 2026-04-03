"""
test_cases.py
─────────────
HOW TO WRITE A TEST CASE
─────────────────────────
1. Define a function  tc_XXX_name(page, reporter)
2. Call  reporter.start_test("TC-XXX", "what this test does")
3. List steps as  ("description", lambda: action(page, ...))
4. Return  reporter.run_steps(steps)
5. Add the function to TEST_CASES at the bottom

Example:
    def tc_010_search(page, reporter):
        reporter.start_test("TC-010", "Search for a risk item")
        steps = [
            ("Go to search page",           lambda: go_to(page, APP_URL + "/search")),
            ("Type keyword in search box",  lambda: fill_input(page, "#search", "data risk")),
            ("Click the Search button",     lambda: click_button(page, "Search")),
            ("Verify result is shown",      lambda: check_text(page, ".results", "data risk")),
        ]
        return reporter.run_steps(steps)

AVAILABLE ACTIONS
──────────────────────────────────────────────────────────────────
  go_to(page, url)                          navigate to a URL
  wait_for_page(page)                       wait for network to settle
  wait_for_url(page, "**pattern**")         wait until URL matches
  check_url(page, "/expected")              assert URL contains text

  click_button(page, "Save")                click by visible text
  click_element(page, "#selector")          click by CSS selector
  click_all(page, ".selector")              click every matching element
  click_checkbox(page, "#checkbox")         tick a checkbox or radio

  fill_input(page, "#selector", "value")    type into one input
  fill_all(page, ".selector", "value")      type into all matching inputs
  clear_input(page, "#selector")            clear an input
  select_dropdown(page, "#sel", "option")   choose from any dropdown
  multi_select(page, "#sel", ["a", "b"])    choose multiple options

  get_text(page, ".selector")               read element text
  get_attribute(page, ".el", "attr")        read an element attribute

  check_visible(page, ".selector")          assert element is visible
  check_text(page, ".selector", "value")    assert element contains text
  check_count(page, ".selector", 5)         assert number of elements
  check_title(page, "My App")               assert page title

  wait_for(page, ".selector")               wait for element to appear
──────────────────────────────────────────────────────────────────
"""

from config import APP_URL, SSO_EMAIL
from actions import (
    go_to, wait_for_page, wait_for_url, check_url,
    click_button, click_element, click_all, click_checkbox,
    fill_input, fill_all, clear_input, select_dropdown, multi_select,
    get_text, get_attribute,
    check_visible, check_text, check_count, check_title,
    wait_for,
)


# ─────────────────────────────────────────────────────────────────────────────
# TC-001 : Open application and verify home page
# ─────────────────────────────────────────────────────────────────────────────
def tc_001_open_app(page, reporter):
    reporter.start_test("TC-001", "Open application and verify home page loads")
    steps = [
        ("Go to the application URL",
         lambda: go_to(page, APP_URL)),

        ("Verify URL loaded correctly",
         lambda: check_url(page, APP_URL)),

        ("Verify page header is visible",
         lambda: check_visible(page, "header, h1")),
    ]
    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-002 : Login via Microsoft SSO
# ─────────────────────────────────────────────────────────────────────────────
def tc_002_login(page, reporter):
    reporter.start_test("TC-002", "Login via Microsoft SSO")
    steps = [
        ("Click the Login button",
         lambda: click_button(page, "Login")),

        ("Wait for Microsoft login page",
         lambda: wait_for_url(page, "**login.microsoftonline.com**", timeout=15_000)),

        (f"Click SSO account for {SSO_EMAIL}",
         lambda: click_element(page, f"[data-test-id='{SSO_EMAIL}']")),

        ("Wait for app to load after login",
         lambda: wait_for_url(page, "**/home**", timeout=20_000)),

        ("Verify home page loaded",
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
         lambda: click_button(page, "Comprehensive Risk Assessment")),

        ("Verify assessment page loaded",
         lambda: check_url(page, "assessment")),

        ("Verify page heading is visible",
         lambda: check_visible(page, "h1, h2")),
    ]
    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-004 : Select Qualitative Assessment card
# ─────────────────────────────────────────────────────────────────────────────
def tc_004_select_qualitative_assessment(page, reporter):
    reporter.start_test("TC-004", "Select Run Qualitative Assessment card")
    steps = [
        ("Verify assessment cards are visible",
         lambda: check_visible(page, 'div[class*="cardContainer"]')),

        ("Click the Qualitative Assessment card",
         lambda: click_element(page, 'div[class*="cardContainer"]:has(p[data-testid="Qualitative Assessment"])')),

        ("Wait for next page to load",
         lambda: wait_for_page(page)),
    ]
    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-005 : Select OS Summary from dropdown
# ─────────────────────────────────────────────────────────────────────────────
def tc_005_select_os_summary(page, reporter):
    reporter.start_test("TC-005", "Select OS Summary from assessment type dropdown")
    steps = [
        ("Verify the dropdown is visible",
         lambda: check_visible(page, "div.react-select__control")),

        ("Select OS Summary from the dropdown",
         lambda: select_dropdown(page, "div.react-select__control", "OS-SUMMARY")),

        ("Verify OS Summary is selected",
         lambda: check_text(page, "div.react-select__single-value", "Summary")),
    ]
    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-006 : Open questionnaire via Assessment icon
# ─────────────────────────────────────────────────────────────────────────────
def tc_006_open_questionnaire(page, reporter):
    reporter.start_test("TC-006", "Open questionnaire via Assessment icon")
    steps = [
        ("Verify Assessment icon is visible",
         lambda: check_visible(page, '[aria-label="Assessment"]')),

        ("Click Assessment icon",
         lambda: click_element(page, '[aria-label="Assessment"]')),

        ("Wait for questionnaire questions to load",
         lambda: wait_for(page, ".accordionItem", timeout=10_000)),
    ]
    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-007 : Answer all questionnaire questions
# ─────────────────────────────────────────────────────────────────────────────
def tc_007_answer_all_questions(page, reporter):
    reporter.start_test("TC-007", "Answer all questionnaire questions")
    steps = [
        ("Verify questions are loaded on the page",
         lambda: check_visible(page, ".accordionItem")),

        ("Expand all question sections",
         lambda: click_all(page, ".accordionItem[aria-expanded='false']")),

        ("Click Yes on all Yes/No questions",
         lambda: click_all(page, ".yesNoGroup [for*='option-Yes']")),

        ("Fill in all open text fields with answer",
         lambda: fill_all(page, "textarea.infraTextarea", "Answered")),
    ]
    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TC-008 : Save the completed assessment
# ─────────────────────────────────────────────────────────────────────────────
def tc_008_save_assessment(page, reporter):
    reporter.start_test("TC-008", "Save the completed assessment")
    steps = [
        ("Click the Save button",
         lambda: click_button(page, "Save")),

        ("Wait for save to complete",
         lambda: wait_for_page(page)),

        ("Verify success message appears",
         lambda: wait_for(page, "[data-testid='toast-success'], .success-banner",
                          timeout=8_000)),

        ("Read the success message",
         lambda: get_text(page, "[data-testid='toast-success'], .success-banner")),
    ]
    return reporter.run_steps(steps)


# ─────────────────────────────────────────────────────────────────────────────
# TEST_CASES — execution order
# Add new test case functions here to include them in the run.
# ─────────────────────────────────────────────────────────────────────────────
TEST_CASES = [
    tc_001_open_app,
    tc_002_login,
    tc_003_navigate_to_risk_assessment,
    tc_004_select_qualitative_assessment,
    tc_005_select_os_summary,
    tc_006_open_questionnaire,
    tc_007_answer_all_questions,
    tc_008_save_assessment,
]
