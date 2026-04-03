"""
page_actions.py — Complex multi-step app interactions.

These are available for advanced use cases that cannot be expressed
as a single generic action. test_cases.py does not import from here
— all test steps use actions.py directly.
"""

from actions import click_element, select_dropdown, wait_for_page, log

# Label selectors tried in priority order when reading a question's text
_LABEL_SELECTORS = ["label", "p[class*='question']", "span[class*='question']", "p"]


def collect_questions(page) -> list[dict]:
    """
    Expand every accordion section and return a list of question metadata dicts.
    Each dict: num, parent_idx, parent_label, child_idx, question_label, type, panel_id
    """
    log("collect_questions: scanning accordion sections")

    questions: list[dict] = []
    num = 0

    parents = page.locator(".accordionItem").all() or \
              page.locator('[data-testid="parent-question"]').all()

    for p_idx, header in enumerate(parents):
        parent_label  = _safe_text(header)
        aria_expanded = header.get_attribute("aria-expanded")
        panel_id      = header.get_attribute("aria-controls") or ""

        if aria_expanded == "false":
            header.click()
            if panel_id:
                page.locator(f"#{panel_id}").wait_for(state="visible", timeout=3_000)

        panel    = page.locator(f"#{panel_id}") if panel_id else header.locator("..").last
        children = panel.locator(".childCard").all()

        for c_idx, child in enumerate(children):
            num += 1
            yes_no = child.locator(".yesNoGroup")
            if yes_no.count() > 0:
                has_na = yes_no.locator('[for*="option"]').filter(has_text="NA").count()
                q_type = "na_only" if has_na else "yes_no"
            else:
                q_type = "text" if child.locator("textarea.infraTextarea").count() else "unknown"

            questions.append({
                "num":            num,
                "parent_idx":     p_idx,
                "parent_label":   parent_label,
                "child_idx":      c_idx,
                "question_label": _read_label(child) or f"Question {num}",
                "type":           q_type,
                "panel_id":       panel_id,
            })

    log(f"collect_questions: {len(questions)} found")
    return questions


def answer_single_question(page, q: dict) -> bool:
    """Answer exactly one question from a collect_questions() dict."""
    panel  = page.locator(f"#{q['panel_id']}")
    child  = panel.locator(".childCard").nth(q["child_idx"])
    label  = q["question_label"][:60]

    if child.count() == 0:
        raise AssertionError(f"child_idx={q['child_idx']} not found in panel '{q['panel_id']}'")

    if q["type"] == "yes_no":
        log(f"  Q{q['num']:02d} yes_no → Yes  [{label}]")
        child.locator(".yesNoGroup [for*='option-Yes']").first.click()
    elif q["type"] == "text":
        log(f"  Q{q['num']:02d} text   → fill  [{label}]")
        child.locator("textarea.infraTextarea").first.fill("Answered")
    elif q["type"] == "na_only":
        log(f"  Q{q['num']:02d} na_only → skip  [{label}]")
    else:
        raise AssertionError(f"Unknown type '{q['type']}' for Q{q['num']}")

    return True


# ── Private helpers ───────────────────────────────────────────────────────────

def _read_label(child) -> str:
    for sel in _LABEL_SELECTORS:
        el = child.locator(sel).first
        if el.count() and el.is_visible():
            return el.inner_text().strip()[:120]
    return ""

def _safe_text(locator, *, max_len: int = 80) -> str:
    try:
        return locator.inner_text().strip()[:max_len]
    except Exception:
        return ""
