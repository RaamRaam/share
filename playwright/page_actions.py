"""
page_actions.py — App-specific page interactions.

Each function is one logical app action and raises on failure
so reporter.run_steps() can catch and log it uniformly.
These call actions.py helpers where appropriate.
"""

from actions import (
    click_by_selector,
    wait_for_load,
    _log,
)


# ── Navigation ───────────────────────────────────────────────────────────────

def click_comprehensive_risk_assessment(page):
    _log("Navigating to Comprehensive Risk Assessment")
    page.locator("text=Comprehensive Risk Assessment").click()
    wait_for_load(page)


def click_run_qualitative_assessment(page):
    _log("Selecting Run Qualitative Assessment card")
    cards = page.locator('div[class*="cardContainer"]')
    for i in range(cards.count()):
        card = cards.nth(i)
        if (
            card.locator('p[data-testid="Questionnaires"]').count() > 0
            and card.locator('p[data-testid="Qualitative Assessment"]').count() > 0
        ):
            card.click()
            wait_for_load(page)
            return
    raise AssertionError("Run Qualitative Assessment card not found")


def select_os_summary(page):
    _log("Opening react-select and choosing OS-SUMMARY")
    page.locator("div.react-select__control").click()
    option = page.locator('div.react-select__option[id$="-OS-SUMMARY"]').first
    option.wait_for(state="visible")
    option.click()
    wait_for_load(page)


def click_assessment_icon(page):
    _log("Clicking Assessment icon")
    click_by_selector(page, 'span[aria-label="Assessment"]')
    wait_for_load(page)


# ── Questionnaire ─────────────────────────────────────────────────────────────

def answer_all_questions(page):
    """
    Outer loop : parent questions (.accordionItem)
    Inner loop : sub-questions (.childCard) within each parent

    CASE 1 — Yes/No group  → click Yes (skip if NA-only)
    CASE 2 — Text/textarea → fill with "Answered"
    """
    _log("Starting answer_all_questions")

    parent_selector = ".accordionItem"
    fallback_selector = '[data-testid="parent-question"]'

    parents = page.locator(parent_selector).all()
    if not parents:
        parents = page.locator(fallback_selector).all()

    for p_idx in range(len(parents)):
        # Re-query each iteration to avoid stale references
        parents = page.locator(parent_selector).all() or page.locator(fallback_selector).all()
        header = parents[p_idx]

        if header.get_attribute("aria-expanded") == "false":
            header.click()
            page.wait_for_timeout(300)

        panel_id = header.get_attribute("aria-controls")
        panel = page.locator(f"#{panel_id}")

        sub_questions = panel.locator(".childCard").all()
        _log(f"  Parent [{p_idx + 1}] → {len(sub_questions)} sub-question(s)")

        for c_idx in range(len(sub_questions)):
            sub_questions = panel.locator(".childCard").all()
            child = sub_questions[c_idx]
            yes_no_group = child.locator(".yesNoGroup")

            if yes_no_group.count() > 0:
                # Skip NA-only questions
                na_label = yes_no_group.locator('[for*="option"]').filter(has_text="NA")
                if na_label.count():
                    continue
                yes_no_group.locator('[for*="option-Yes"]').first.click()

            else:
                textareas = child.locator("textarea.infraTextarea")
                if textareas.count():
                    textareas.first.fill("Answered")

    _log("answer_all_questions complete")


# ── Save ──────────────────────────────────────────────────────────────────────

def click_save(page):
    _log("Clicking Save")
    page.locator('input[type="text"]').nth(17).click()
    wait_for_load(page)
    _log("Save complete")
