"""
actions.py — Reusable Playwright action helpers.

Every function either:
  • returns a value (extract_*, get_*)
  • returns True on success
  • raises AssertionError / PlaywrightTimeoutError on failure

This lets reporter.run_steps() catch failures uniformly.

Available actions
─────────────────
Navigation
  navigate(page, url, *, wait_until)

Clicking
  click_button(page, *, selector, text, nth)
  click_button_ci(page, texts)           ← case-insensitive text match
  click_by_selector(page, selector, *, nth)

URL / page checks
  check_url(page, expected, *, contains)
  check_title(page, expected, *, contains)
  wait_for_url(page, pattern, *, timeout)

Inputs
  populate_textbox(page, selector, text, *, clear_first, nth)
  clear_textbox(page, selector, *, nth)

Dropdowns
  choose_dropdown(page, selector, option_text, *, nth)   ← native <select>
  choose_react_dropdown(page, container_sel, option_text, *, nth)
  multi_select_dropdown(page, container_sel, options, *, nth)

Content / assertions
  extract_div_content(page, selector, *, nth)  → str
  get_element_attribute(page, selector, attr, *, nth)  → str
  check_value_in_div(page, selector, expected, *, contains, nth)
  check_element_visible(page, selector, *, nth)
  check_element_count(page, selector, expected_count)

Waiting
  wait_for_element(page, selector, *, timeout, state)
  wait_for_load(page, *, state)
"""

# ── internal print helper ────────────────────────────────────────────────────

def _log(msg: str) -> None:
    print(f"    · {msg}")


# ── Navigation ───────────────────────────────────────────────────────────────

def navigate(page, url: str, *, wait_until: str = "networkidle") -> bool:
    """Go to a URL and wait for the page to settle."""
    _log(f"navigate → {url}")
    page.goto(url, wait_until=wait_until)
    return True


# ── Clicking ─────────────────────────────────────────────────────────────────

def click_button(page, *, selector: str = None, text: str = None, nth: int = 0) -> bool:
    """
    Click an element.
    Provide either `selector` (CSS/XPath) or `text` (exact visible text).
    """
    if selector:
        _log(f"click_button selector='{selector}' nth={nth}")
        page.locator(selector).nth(nth).click()
    elif text:
        _log(f"click_button text='{text}' nth={nth}")
        page.get_by_text(text, exact=True).nth(nth).click()
    else:
        raise ValueError("click_button requires selector or text")
    return True


def click_button_ci(page, texts: list[str]) -> bool:
    """Click the first element whose normalised text matches any entry in `texts` (case-insensitive)."""
    for t in texts:
        el = page.locator(
            f"xpath=//*[translate(normalize-space(text()),"
            f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='{t.lower()}']"
        )
        if el.count():
            _log(f"click_button_ci matched '{t}'")
            el.first.click()
            return True
    raise AssertionError(f"No clickable element found for texts: {texts}")


def click_by_selector(page, selector: str, *, nth: int = 0) -> bool:
    """Click an element by CSS selector."""
    _log(f"click_by_selector '{selector}' nth={nth}")
    page.locator(selector).nth(nth).click()
    return True


# ── URL / page checks ─────────────────────────────────────────────────────────

def check_url(page, expected: str, *, contains: bool = True) -> bool:
    """
    Assert the current URL contains (default) or exactly equals `expected`.
    Raises AssertionError on mismatch.
    """
    current = page.url
    _log(f"check_url  current='{current}'  expected='{expected}'  contains={contains}")
    if contains:
        assert expected in current, f"URL check failed — '{expected}' not in '{current}'"
    else:
        assert current == expected, f"URL check failed — expected '{expected}', got '{current}'"
    return True


def check_title(page, expected: str, *, contains: bool = True) -> bool:
    """Assert the page <title> contains (or equals) `expected`."""
    title = page.title()
    _log(f"check_title  title='{title}'  expected='{expected}'")
    if contains:
        assert expected in title, f"Title check failed — '{expected}' not in '{title}'"
    else:
        assert title == expected, f"Title check failed — expected '{expected}', got '{title}'"
    return True


def wait_for_url(page, pattern: str, *, timeout: int = 10_000) -> bool:
    """Wait until the URL matches a glob pattern."""
    _log(f"wait_for_url pattern='{pattern}'")
    page.wait_for_url(pattern, timeout=timeout)
    return True


# ── Inputs ────────────────────────────────────────────────────────────────────

def populate_textbox(page, selector: str, text: str,
                     *, clear_first: bool = True, nth: int = 0) -> bool:
    """
    Fill a text input or textarea.
    `clear_first=True` clears any existing value before typing.
    """
    _log(f"populate_textbox '{selector}' nth={nth}  value='{text}'")
    el = page.locator(selector).nth(nth)
    el.wait_for(state="visible")
    if clear_first:
        el.fill("")
    el.fill(text)
    return True


def clear_textbox(page, selector: str, *, nth: int = 0) -> bool:
    """Clear a text input."""
    _log(f"clear_textbox '{selector}' nth={nth}")
    page.locator(selector).nth(nth).fill("")
    return True


# ── Dropdowns ─────────────────────────────────────────────────────────────────

def choose_dropdown(page, selector: str, option_text: str, *, nth: int = 0) -> bool:
    """
    Select an option from a native HTML <select> element by visible text.
    """
    _log(f"choose_dropdown '{selector}'  option='{option_text}'")
    page.locator(selector).nth(nth).select_option(label=option_text)
    return True


def choose_react_dropdown(page, container_sel: str, option_text: str, *, nth: int = 0) -> bool:
    """
    Select an option from a react-select (or similar custom) dropdown.
    Steps: open the control → wait for menu → click matching option.
    """
    _log(f"choose_react_dropdown '{container_sel}'  option='{option_text}'")
    control = page.locator(f"{container_sel} .react-select__control, "
                           f"{container_sel}.react-select__control").nth(nth)
    control.click()

    # Wait for the menu to open then click the matching option
    menu = page.locator(f"{container_sel} .react-select__menu, "
                        f"{container_sel}.react-select__menu").nth(nth)
    menu.wait_for(state="visible")

    option = menu.get_by_text(option_text, exact=False).first
    assert option.count() or option.is_visible(), \
        f"Option '{option_text}' not found in dropdown '{container_sel}'"
    option.click()
    return True


def multi_select_dropdown(page, container_sel: str, options: list[str], *, nth: int = 0) -> bool:
    """
    Select multiple options in a react-select multi-select.
    Opens the control once and clicks each option in sequence.
    """
    _log(f"multi_select_dropdown '{container_sel}'  options={options}")
    control = page.locator(f"{container_sel} .react-select__control, "
                           f"{container_sel}.react-select__control").nth(nth)

    for opt in options:
        control.click()
        menu = page.locator(f"{container_sel} .react-select__menu, "
                            f"{container_sel}.react-select__menu").nth(nth)
        menu.wait_for(state="visible")
        item = menu.get_by_text(opt, exact=False).first
        assert item.is_visible(), f"Option '{opt}' not found in multi-select '{container_sel}'"
        item.click()
        page.wait_for_timeout(200)   # brief settle between selections

    return True


# ── Content / assertions ──────────────────────────────────────────────────────

def extract_div_content(page, selector: str, *, nth: int = 0) -> str:
    """Return the inner text of an element. Raises if not found."""
    _log(f"extract_div_content '{selector}' nth={nth}")
    el = page.locator(selector).nth(nth)
    el.wait_for(state="visible")
    text = el.inner_text().strip()
    _log(f"  → '{text}'")
    return text


def get_element_attribute(page, selector: str, attribute: str, *, nth: int = 0) -> str:
    """Return the value of an element's HTML attribute."""
    _log(f"get_element_attribute '{selector}' attr='{attribute}' nth={nth}")
    value = page.locator(selector).nth(nth).get_attribute(attribute) or ""
    _log(f"  → '{value}'")
    return value


def check_value_in_div(page, selector: str, expected: str,
                       *, contains: bool = True, nth: int = 0) -> bool:
    """
    Assert that an element's text contains (default) or equals `expected`.
    Raises AssertionError on mismatch.
    """
    actual = extract_div_content(page, selector, nth=nth)
    _log(f"check_value_in_div  actual='{actual}'  expected='{expected}'  contains={contains}")
    if contains:
        assert expected in actual, \
            f"Value check failed — '{expected}' not found in '{actual}'"
    else:
        assert actual == expected, \
            f"Value check failed — expected '{expected}', got '{actual}'"
    return True


def check_element_visible(page, selector: str, *, nth: int = 0) -> bool:
    """Assert element exists and is visible. Raises AssertionError otherwise."""
    _log(f"check_element_visible '{selector}' nth={nth}")
    el = page.locator(selector).nth(nth)
    assert el.count() > 0, f"Element not found: '{selector}'"
    assert el.is_visible(), f"Element not visible: '{selector}'"
    return True


def check_element_count(page, selector: str, expected_count: int) -> bool:
    """Assert the number of elements matching `selector`."""
    _log(f"check_element_count '{selector}'  expected={expected_count}")
    actual = page.locator(selector).count()
    assert actual == expected_count, \
        f"Count check failed — expected {expected_count}, got {actual} for '{selector}'"
    return True


# ── Waiting ───────────────────────────────────────────────────────────────────

def wait_for_element(page, selector: str, *, timeout: int = 5_000, state: str = "visible") -> bool:
    """Wait for an element to reach a given state (visible / hidden / attached / detached)."""
    _log(f"wait_for_element '{selector}'  state='{state}'  timeout={timeout}ms")
    page.locator(selector).first.wait_for(state=state, timeout=timeout)
    return True


def wait_for_load(page, *, state: str = "networkidle") -> bool:
    """Wait for the page network / DOM to settle."""
    _log(f"wait_for_load  state='{state}'")
    page.wait_for_load_state(state)
    return True
