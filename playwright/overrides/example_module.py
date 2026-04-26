"""
overrides/example_module.py — Example override for a "dashboard" module.

Copy and rename this file to override actions for any module in your app.
The MODULE_NAME must match either:
  • the `module` field in the Excel/YAML test case, OR
  • the first URL path segment (auto-detected)

Rename this file to match your module (e.g. settings.py, reports.py).
"""

from actions import log, click as _generic_click, fill_input as _generic_fill


MODULE_NAME = "dashboard"   # ← change to your module path segment


# ── Override: click ───────────────────────────────────────────────────────────

def _click(page, text: str, **kwargs) -> bool:
    """
    Dashboard-specific click: dismisses any loading overlay before clicking.
    Falls back to the generic click once the overlay is gone.
    """
    log(f"[OVERRIDE dashboard] click '{text}'")
    overlay = page.locator(".loading-overlay, [data-testid='spinner']")
    if overlay.count() and overlay.is_visible():
        log("  waiting for loading overlay to disappear …")
        overlay.wait_for(state="hidden", timeout=10_000)
    return _generic_click(page, text, **kwargs)


# ── Override: fill_input ──────────────────────────────────────────────────────

def _fill_input(page, value: str, **kwargs) -> bool:
    """
    Dashboard-specific fill: scrolls the element into view first.
    """
    log(f"[OVERRIDE dashboard] fill_input value='{value}'")
    # (Optional) scroll to input before filling — useful for long pages
    placeholder = kwargs.get("placeholder")
    if placeholder:
        page.get_by_placeholder(placeholder, exact=False).first.scroll_into_view_if_needed()
    return _generic_fill(page, value, **kwargs)


# ── Export ────────────────────────────────────────────────────────────────────

OVERRIDES = {
    "click":      _click,
    "fill_input": _fill_input,
}
