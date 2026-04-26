"""
actions.py — Generic Playwright actions used by the YAML test runner.

Design rules
─────────────
• Every function accepts (page, **keyword-params) so the YAML runner can call
  fn(page, **step["params"]) without special-casing anything.
• Every function returns True on success or raises on failure.
• The `nth` param (default 0) selects among multiple matches.
• Functions are intentionally flat — no hidden waits beyond what Playwright
  already provides through its auto-wait mechanism.

AVAILABLE FUNCTIONS (for Excel step_function column)
─────────────────────────────────────────────────────────────────────────────
  Navigation
    go_to(url)                        navigate and wait for networkidle
    wait_for_page()                   wait for network to settle
    wait_for_url(pattern)             wait until URL matches glob
    check_url(expected)               assert URL contains text

  Clicking
    click(text, exact=False,          click any element by visible text;
          validate_url=None, nth=0)   optionally assert URL afterward
    click_element(selector, nth=0)    click by CSS selector
    click_all(selector)               click every visible match
    click_checkbox(selector, nth=0)   tick a checkbox / radio

  Filling inputs
    fill_input(value,                 fill a text input / textarea;
               placeholder=None,     target by placeholder text …
               label=None,           … by adjacent label text …
               selector=None,        … or by CSS selector
               nth=0)
    fill_all(selector, value)         fill all matching inputs
    clear_input(selector, nth=0)      clear an input

  Dropdowns
    select_dropdown(selector, value,  choose from native or react-select
                    nth=0)
    multi_select(selector, values,    select multiple options
                 nth=0)

  Search / combo box
    search_input(placeholder, value)  find search box by placeholder,
                                      type value, select or press Enter

  Reading
    get_text(selector, nth=0)         return visible text of element
    get_adjacent_text(label, nth=0)   return text of element next to label
    get_attribute(selector,           return HTML attribute value
                  attribute, nth=0)

  Table
    get_row_text(search_text)         find row by cell text, return all cells
    click_row_icon(search_text,       find row by text, click icon by index
                   icon_index=0,      or by aria-label / title name
                   icon_name=None)

  Verification
    check_visible(selector, nth=0)    assert element is visible
    check_text(selector, expected,    assert element text contains value
               nth=0)
    check_title(expected)             assert page <title> contains text
    check_count(selector, expected)   assert element count

  Waiting
    wait_for(selector, timeout=8000)  wait for element to appear

  Demo
    demo_mouse_move(steps=10,         sweep the cursor across the page
                    duration_ms=1000) to visualise automation
─────────────────────────────────────────────────────────────────────────────
"""

import math
import time

# ── Internal helper ───────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"    · {msg}")


# ── Navigation ────────────────────────────────────────────────────────────────

def go_to(page, url: str) -> bool:
    log(f"go_to → {url}")
    page.goto(url, wait_until="networkidle")
    return True


def wait_for_page(page) -> bool:
    log("wait_for_page")
    page.wait_for_load_state("networkidle")
    return True


def wait_for_url(page, pattern: str, *, timeout: int = 10_000) -> bool:
    log(f"wait_for_url '{pattern}'")
    page.wait_for_url(pattern, timeout=timeout)
    return True


def check_url(page, expected: str) -> bool:
    current = page.url
    log(f"check_url  current='{current}'  expected='{expected}'")
    assert expected in current, f"URL check failed — '{expected}' not in '{current}'"
    return True


# ── Clicking ──────────────────────────────────────────────────────────────────

def click(page, text: str, *, exact: bool = False, validate_url: str = None,
          nth: int = 0) -> bool:
    """
    Click any element — button, link, span, div, card — by visible text.

    Tries strategies in order:
      1. ARIA roles: button, link, menuitem, tab, option  (exact or contains)
      2. Exact own-text match on any element
      3. <p> tag containing text → click its parent container
      4. Any element whose full inner text contains the search text
    Optionally asserts the resulting URL contains `validate_url`.
    """
    t   = text.strip().lower()
    _TX = ("translate(normalize-space(text()),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")
    _TC = ("translate(normalize-space(.),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")

    log(f"click '{text}' exact={exact} nth={nth}")

    # 1 — ARIA roles (Playwright getByRole handles accessible name)
    for role in ("button", "link", "menuitem", "tab", "option"):
        try:
            el = page.get_by_role(role, name=text, exact=exact).nth(nth)
            if el.count() and el.is_visible():
                el.click()
                _maybe_validate_url(page, validate_url)
                return True
        except Exception:
            pass

    # 2 — exact own-text match on any element
    exact_sel = f"xpath=//*[{_TX}='{t}']"
    el = page.locator(exact_sel).nth(nth)
    if el.count() and el.is_visible():
        el.click()
        _maybe_validate_url(page, validate_url)
        return True

    # 3 — <p> contains text → click parent container (cards, list items)
    p_sel = f"xpath=//p[contains({_TX},'{t}')]"
    el = page.locator(p_sel).nth(nth)
    if el.count() and el.is_visible():
        el.locator("xpath=..").click()
        _maybe_validate_url(page, validate_url)
        return True

    # 4 — any element whose full subtree contains the text
    broad = page.locator(
        f"xpath=//*[contains({_TC},'{t}')][not(self::html)][not(self::body)]"
    ).nth(nth)
    assert broad.count() > 0, f"No element found containing text '{text}'"
    broad.click()
    _maybe_validate_url(page, validate_url)
    return True


def _maybe_validate_url(page, validate_url: str | None) -> None:
    if validate_url:
        page.wait_for_url(f"**{validate_url}**", timeout=10_000)
        log(f"  ✓ URL contains '{validate_url}'")


def click_element(page, selector: str, *, nth: int = 0) -> bool:
    log(f"click_element '{selector}' nth={nth}")
    page.locator(selector).nth(nth).click()
    return True


def click_all(page, selector: str) -> bool:
    log(f"click_all '{selector}'")
    elements = page.locator(selector).all()
    assert len(elements) > 0, f"No elements found for '{selector}'"
    for el in elements:
        if el.is_visible():
            el.click()
    return True


def click_checkbox(page, selector: str, *, nth: int = 0) -> bool:
    log(f"click_checkbox '{selector}' nth={nth}")
    page.locator(selector).nth(nth).click()
    return True


# ── Forms ─────────────────────────────────────────────────────────────────────

def fill_input(page, value: str, *,
               placeholder: str = None,
               label: str = None,
               selector: str = None,
               nth: int = 0) -> bool:
    """
    Clear and type `value` into a text input or textarea.

    Provide exactly one targeting strategy:
      placeholder — matches the input's placeholder attribute (case-insensitive)
      label       — matches adjacent label text or parent div text, then finds
                    the input inside; falls back to Playwright get_by_label
      selector    — raw CSS / XPath selector
    """
    log(f"fill_input value='{value}' placeholder={placeholder!r} "
        f"label={label!r} selector={selector!r}")

    if placeholder:
        el = page.get_by_placeholder(placeholder, exact=False).nth(nth)

    elif label:
        # Try standard HTML <label> association first
        el = page.get_by_label(label, exact=False)
        if not (el.count() and el.is_visible()):
            # Fall back: input inside or after a container with the label text
            t   = label.strip().lower()
            _TC = ("translate(normalize-space(.),"
                   "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")
            el = page.locator(
                f"xpath=//*[contains({_TC},'{t}')]//following::input[1] | "
                f"//*[contains({_TC},'{t}')]//input[1]"
            ).nth(nth)

    elif selector:
        el = page.locator(selector).nth(nth)

    else:
        raise ValueError("fill_input requires one of: placeholder, label, or selector")

    el.wait_for(state="visible")
    el.fill(value)
    return True


def fill_all(page, selector: str, value: str) -> bool:
    log(f"fill_all '{selector}' value='{value}'")
    for el in page.locator(selector).all():
        if el.is_visible():
            el.fill(value)
    return True


def clear_input(page, selector: str, *, nth: int = 0) -> bool:
    log(f"clear_input '{selector}'")
    page.locator(selector).nth(nth).fill("")
    return True


def select_dropdown(page, selector: str, value: str, *, nth: int = 0) -> bool:
    """
    Choose from a native <select> or a custom dropdown (react-select).
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
    log(f"multi_select '{selector}' values={values}")
    control = page.locator(selector).nth(nth)
    for value in values:
        control.click()
        page.get_by_role("option", name=value, exact=False).first.click()
    return True


# ── Search & combo box ────────────────────────────────────────────────────────

def search_input(page, placeholder: str, value: str) -> bool:
    """
    Find a search / combo box by placeholder, type `value`, then either
    select the matching dropdown option or press Enter.
    Works with plain inputs, react-select, and most autocomplete components.
    """
    log(f"search_input placeholder='{placeholder}' value='{value}'")

    # Strategy 1: react-select
    rs_control = page.locator("[class*='react-select__control']").filter(
        has=page.locator("[class*='placeholder']", has_text=placeholder)
    ).first
    if rs_control.count() and rs_control.is_visible():
        log("  → react-select detected")
        rs_control.click()
        rs_control.locator("input").first.fill(value)
        option = page.locator("[class*='react-select__option']").filter(
            has_text=value
        ).first
        option.wait_for(state="visible", timeout=3_000)
        option.click()
        return True

    # Strategy 2: plain input with placeholder
    el = page.get_by_placeholder(placeholder, exact=False)
    el.wait_for(state="visible")
    el.fill(value)

    dropdown = page.locator("[role='listbox'] [role='option'], [role='option'], [class*='option']")
    try:
        dropdown.first.wait_for(state="visible", timeout=2_000)
        option = dropdown.filter(has_text=value).first
        if option.count() and option.is_visible():
            option.click()
            return True
    except Exception:
        pass
    el.press("Enter")
    return True


# ── Reading ───────────────────────────────────────────────────────────────────

def get_text(page, selector: str, *, nth: int = 0) -> str:
    log(f"get_text '{selector}'")
    el = page.locator(selector).nth(nth)
    el.wait_for(state="visible")
    text = el.inner_text().strip()
    log(f"  → '{text}'")
    return text


def get_adjacent_text(page, label: str, *, nth: int = 0) -> str:
    """
    Find a label / heading on the page and return the text of the adjacent
    element that contains the displayed value.

    Supports common layout patterns:
      • <dt> / <dd>  definition lists
      • <td> / <td>  table cells
      • <th> / <td>  table header + data cell
      • sibling span / div  (key-value pairs)
      • parent's next sibling  (wrapped key-value)
    """
    log(f"get_adjacent_text label='{label}'")
    t   = label.strip().lower()
    _TX = ("translate(normalize-space(.),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")

    xpaths = [
        f"xpath=//dt[contains({_TX},'{t}')]/following-sibling::dd[1]",
        f"xpath=//td[contains({_TX},'{t}')]/following-sibling::td[1]",
        f"xpath=//th[contains({_TX},'{t}')]/following-sibling::td[1]",
        f"xpath=//*[contains({_TX},'{t}')]/following-sibling::*[1]",
        f"xpath=//*[contains({_TX},'{t}')]/../following-sibling::*[1]",
        f"xpath=//*[contains({_TX},'{t}')]/following::*[1]",
    ]

    for xpath in xpaths:
        try:
            el = page.locator(xpath).nth(nth)
            if el.count() and el.is_visible():
                text = el.inner_text().strip()
                log(f"  → '{text}'")
                return text
        except Exception:
            pass

    raise AssertionError(f"Could not find adjacent text for label '{label}'")


def get_attribute(page, selector: str, attribute: str, *, nth: int = 0) -> str:
    log(f"get_attribute '{selector}' attr='{attribute}'")
    value = page.locator(selector).nth(nth).get_attribute(attribute) or ""
    log(f"  → '{value}'")
    return value


# ── Table ─────────────────────────────────────────────────────────────────────

def get_row_text(page, search_text: str) -> str:
    """
    Find the first <tr> that contains `search_text` in any <td>,
    return all cells joined by ' | '.
    """
    log(f"get_row_text search='{search_text}'")
    t   = search_text.lower()
    _TC = ("translate(normalize-space(.),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")
    row = page.locator(f"xpath=//tr[td[contains({_TC},'{t}')]]").first
    assert row.count() > 0, f"No table row found containing '{search_text}'"
    text = " | ".join(c.inner_text().strip() for c in row.locator("td").all())
    log(f"  → '{text}'")
    return text


def click_row_icon(page, search_text: str, icon_index: int = 0,
                   icon_name: str = None) -> bool:
    """
    Find the first <tr> containing `search_text`, then click an icon inside it.

    icon_name  — click the icon whose aria-label or title matches this text
    icon_index — (fallback) click the nth icon when icon_name is not given

    Icons matched: button, [role='button'], [aria-label], svg, img, i
    """
    log(f"click_row_icon search='{search_text}' "
        f"icon_index={icon_index} icon_name={icon_name!r}")
    t   = search_text.lower()
    _TC = ("translate(normalize-space(.),"
           "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')")
    row = page.locator(f"xpath=//tr[td[contains({_TC},'{t}')]]").first
    assert row.count() > 0, f"No table row found containing '{search_text}'"

    icon_sel = "button, [role='button'], [aria-label], svg, img, i"

    if icon_name:
        name_lower = icon_name.lower()
        for candidate in row.locator(icon_sel).all():
            for attr in ("aria-label", "title", "alt"):
                val = (candidate.get_attribute(attr) or "").lower()
                if name_lower in val:
                    candidate.click()
                    return True
        raise AssertionError(
            f"No icon with name '{icon_name}' in row containing '{search_text}'"
        )

    icon = row.locator(icon_sel).nth(icon_index)
    assert icon.count() > 0, \
        f"No icon at index {icon_index} in row containing '{search_text}'"
    icon.click()
    return True


# ── Verification ──────────────────────────────────────────────────────────────

def check_visible(page, selector: str, *, nth: int = 0) -> bool:
    log(f"check_visible '{selector}'")
    el = page.locator(selector).nth(nth)
    assert el.count() > 0, f"Element not found: '{selector}'"
    assert el.is_visible(),  f"Element not visible: '{selector}'"
    return True


def check_text(page, selector: str, expected: str, *, nth: int = 0) -> bool:
    actual = get_text(page, selector, nth=nth)
    assert expected in actual, \
        f"Text check failed — expected '{expected}' in '{actual}'"
    return True


def check_title(page, expected: str) -> bool:
    title = page.title()
    log(f"check_title  title='{title}'")
    assert expected in title, f"Title check failed — '{expected}' not in '{title}'"
    return True


def check_count(page, selector: str, expected_count: int) -> bool:
    actual = page.locator(selector).count()
    log(f"check_count '{selector}'  expected={expected_count}  actual={actual}")
    assert actual == expected_count, \
        f"Count check failed — expected {expected_count}, got {actual}"
    return True


# ── Waiting ───────────────────────────────────────────────────────────────────

def wait_for(page, selector: str, *, timeout: int = 8_000) -> bool:
    log(f"wait_for '{selector}'")
    page.locator(selector).first.wait_for(state="visible", timeout=timeout)
    return True


# ── Demo ──────────────────────────────────────────────────────────────────────

def demo_mouse_move(page, *, steps: int = 10, duration_ms: int = 1_000) -> bool:
    """
    Sweep the mouse cursor across the viewport in a gentle sine-wave arc.
    Makes it visually clear that automation is running.
    """
    log(f"demo_mouse_move steps={steps} duration_ms={duration_ms}")
    size     = page.viewport_size or {"width": 1280, "height": 720}
    w, h     = size["width"], size["height"]
    interval = max(duration_ms / steps / 1_000, 0.02)
    for i in range(steps):
        t = i / max(steps - 1, 1)
        x = int(w * 0.05 + w * 0.9 * t)
        y = int(h * 0.5 + h * 0.2 * math.sin(t * math.pi * 2))
        page.mouse.move(x, y)
        time.sleep(interval)
    return True
