"""
actions.py — Generic Playwright actions used directly in test_cases.py.

All function names are plain English verbs.
Every function returns True on success or raises on failure.
"""


def log(msg: str) -> None:
    print(f"    · {msg}")


# ── Navigation ────────────────────────────────────────────────────────────────

def go_to(page, url: str) -> bool:
    """Go to a URL and wait for the page to fully load."""
    log(f"go_to → {url}")
    page.goto(url, wait_until="networkidle")
    return True

def wait_for_page(page) -> bool:
    """Wait for all network activity to stop."""
    log("wait_for_page")
    page.wait_for_load_state("networkidle")
    return True

def wait_for_url(page, pattern: str, *, timeout: int = 10_000) -> bool:
    """Wait until the browser URL matches a glob pattern, e.g. '**/home**'."""
    log(f"wait_for_url '{pattern}'")
    page.wait_for_url(pattern, timeout=timeout)
    return True

def check_url(page, expected: str) -> bool:
    """Assert the current URL contains the expected text."""
    current = page.url
    log(f"check_url  current='{current}'  expected='{expected}'")
    assert expected in current, f"URL check failed — '{expected}' not in '{current}'"
    return True


# ── Clicking ──────────────────────────────────────────────────────────────────

def click(page, text: str, *, nth: int = 0) -> bool:
    """
    Click any element — button, link, div, card, or container — by visible text.

    Tries three strategies in order:
      1. Exact text match on any element  (button, a, span, label, div ...)
      2. <p> tag containing the text → clicks its parent container  (cards, list items)
      3. Any element whose full inner text contains the search text  (nested content)
    """
    t   = text.lower()
    _TX = ("translate(normalize-space(text()),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")
    _TC = ("translate(normalize-space(.),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")

    log(f"click '{text}' nth={nth}")

    # 1 — exact own-text match
    exact = page.locator(f"xpath=//*[{_TX}='{t}']").nth(nth)
    if exact.count() and exact.is_visible():
        exact.click()
        return True

    # 2 — <p> contains text → click parent container
    p_tag = page.locator(f"xpath=//p[contains({_TX},'{t}')]").nth(nth)
    if p_tag.count() and p_tag.is_visible():
        p_tag.locator("xpath=..").click()
        return True

    # 3 — any element whose full subtree contains the text
    broad = page.locator(
        f"xpath=//*[contains({_TC},'{t}')][not(self::html)][not(self::body)]"
    ).nth(nth)
    assert broad.count() > 0, f"No element found containing text '{text}'"
    broad.click()
    return True

def click_element(page, selector: str, *, nth: int = 0) -> bool:
    """Click a single element identified by a CSS selector."""
    log(f"click_element '{selector}' nth={nth}")
    page.locator(selector).nth(nth).click()
    return True

def click_all(page, selector: str) -> bool:
    """Click every visible element matching the selector (e.g. expand all accordions)."""
    log(f"click_all '{selector}'")
    elements = page.locator(selector).all()
    assert len(elements) > 0, f"No elements found for '{selector}'"
    for el in elements:
        if el.is_visible():
            el.click()
    return True

def click_checkbox(page, selector: str, *, nth: int = 0) -> bool:
    """Click a checkbox or radio button."""
    log(f"click_checkbox '{selector}' nth={nth}")
    page.locator(selector).nth(nth).click()
    return True


# ── Forms ─────────────────────────────────────────────────────────────────────

def fill_input(page, selector: str, value: str, *, nth: int = 0) -> bool:
    """Clear and type a value into an input box or textarea."""
    log(f"fill_input '{selector}' value='{value}'")
    el = page.locator(selector).nth(nth)
    el.wait_for(state="visible")
    el.fill(value)
    return True

def fill_all(page, selector: str, value: str) -> bool:
    """Type a value into every matching input or textarea on the page."""
    log(f"fill_all '{selector}' value='{value}'")
    elements = page.locator(selector).all()
    for el in elements:
        if el.is_visible():
            el.fill(value)
    return True

def clear_input(page, selector: str, *, nth: int = 0) -> bool:
    """Clear all text from an input box."""
    log(f"clear_input '{selector}'")
    page.locator(selector).nth(nth).fill("")
    return True

def select_dropdown(page, selector: str, value: str, *, nth: int = 0) -> bool:
    """
    Choose a value from a dropdown.
    Works with both native <select> elements and custom dropdowns (react-select).
    """
    log(f"select_dropdown '{selector}' value='{value}'")
    el = page.locator(selector).nth(nth)
    el.wait_for(state="visible")
    tag = el.evaluate("el => el.tagName.toLowerCase()")
    if tag == "select":
        el.select_option(label=value)
    else:
        el.click()
        page.get_by_role("option", name=value, exact=False).first.click()
    return True

def multi_select(page, selector: str, values: list, *, nth: int = 0) -> bool:
    """Select multiple options from a dropdown (react-select multi)."""
    log(f"multi_select '{selector}' values={values}")
    control = page.locator(selector).nth(nth)
    for value in values:
        control.click()
        page.get_by_role("option", name=value, exact=False).first.click()
    return True


# ── Reading ───────────────────────────────────────────────────────────────────

def get_text(page, selector: str, *, nth: int = 0) -> str:
    """Read and return the visible text of an element."""
    log(f"get_text '{selector}'")
    el = page.locator(selector).nth(nth)
    el.wait_for(state="visible")
    text = el.inner_text().strip()
    log(f"  → '{text}'")
    return text

def get_attribute(page, selector: str, attribute: str, *, nth: int = 0) -> str:
    """Read and return an HTML attribute value from an element."""
    log(f"get_attribute '{selector}' attr='{attribute}'")
    value = page.locator(selector).nth(nth).get_attribute(attribute) or ""
    log(f"  → '{value}'")
    return value


# ── Verification ──────────────────────────────────────────────────────────────

def check_visible(page, selector: str, *, nth: int = 0) -> bool:
    """Assert an element is present and visible on the page."""
    log(f"check_visible '{selector}'")
    el = page.locator(selector).nth(nth)
    assert el.count() > 0, f"Element not found: '{selector}'"
    assert el.is_visible(),  f"Element not visible: '{selector}'"
    return True

def check_text(page, selector: str, expected: str, *, nth: int = 0) -> bool:
    """Assert an element's text contains the expected value."""
    actual = get_text(page, selector, nth=nth)
    assert expected in actual, \
        f"Text check failed — expected '{expected}' in '{actual}'"
    return True

def check_title(page, expected: str) -> bool:
    """Assert the page <title> contains the expected text."""
    title = page.title()
    log(f"check_title  title='{title}'")
    assert expected in title, f"Title check failed — '{expected}' not in '{title}'"
    return True

def check_count(page, selector: str, expected_count: int) -> bool:
    """Assert the number of elements matching the selector."""
    actual = page.locator(selector).count()
    log(f"check_count '{selector}'  expected={expected_count}  actual={actual}")
    assert actual == expected_count, \
        f"Count check failed — expected {expected_count}, got {actual}"
    return True


# ── Waiting ───────────────────────────────────────────────────────────────────

def wait_for(page, selector: str, *, timeout: int = 8_000) -> bool:
    """Wait until an element appears on the page."""
    log(f"wait_for '{selector}'")
    page.locator(selector).first.wait_for(state="visible", timeout=timeout)
    return True


# ── Search & Table ────────────────────────────────────────────────────────────

def search_input(page, placeholder: str, value: str) -> bool:
    """
    Find a search box by its placeholder text, type a value, and press Enter.

    Example:
        search_input(page, "Search by name...", "Data Risk")
    """
    log(f"search_input placeholder='{placeholder}' value='{value}'")
    el = page.get_by_placeholder(placeholder)
    el.wait_for(state="visible")
    el.fill(value)
    el.press("Enter")
    return True


def get_row_text(page, search_text: str) -> str:
    """
    Find the first table row (<tr>) that contains search_text in any cell (<td>),
    and return the full text of that row (all cells joined by ' | ').

    Raises AssertionError if no matching row is found.
    """
    log(f"get_row_text search='{search_text}'")
    t = search_text.lower()
    _TX = ("translate(normalize-space(.),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")
    row = page.locator(
        f"xpath=//tr[td[contains({_TX},'{t}')]]"
    ).first
    assert row.count() > 0, f"No table row found containing '{search_text}'"
    cells = row.locator("td").all()
    text  = " | ".join(c.inner_text().strip() for c in cells)
    log(f"  → '{text}'")
    return text


def click_row_icon(page, search_text: str, icon_index: int = 0) -> bool:
    """
    Find the first table row containing search_text, then click the icon
    inside that row at the given index (0 = first icon, 1 = second, etc.).

    Icons are matched as: button, [role='button'], svg, img, i, or any
    element with an aria-label inside the row's cells.

    Raises AssertionError if the row or icon is not found.
    """
    log(f"click_row_icon search='{search_text}' icon_index={icon_index}")
    t = search_text.lower()
    _TX = ("translate(normalize-space(.),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")
    row = page.locator(
        f"xpath=//tr[td[contains({_TX},'{t}')]]"
    ).first
    assert row.count() > 0, f"No table row found containing '{search_text}'"

    # Try buttons / role=button first, then fall back to svg / img / i icons
    icon = row.locator(
        "button, [role='button'], [aria-label], svg, img, i"
    ).nth(icon_index)
    assert icon.count() > 0, \
        f"No icon at index {icon_index} in row containing '{search_text}'"
    icon.click()
    return True
