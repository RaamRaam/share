"""
overrides/__init__.py — Module-level function override registry.

HOW OVERRIDES WORK
───────────────────
Each file in this directory (except __init__.py) is a module override.
It must define:
    MODULE_NAME = "some-module"   # matched against the test case's `module` field
                                  # or the first URL path segment
    OVERRIDES   = {               # dict of function_name → replacement callable
        "click": my_custom_click,
        "fill_input": my_custom_fill,
    }

WRITING AN OVERRIDE
────────────────────
    # overrides/my_module.py

    from actions import log, click   # import helpers / default fns as needed

    MODULE_NAME = "my_module"

    def _my_click(page, text, **kwargs):
        log(f"[OVERRIDE my_module] click '{text}'")
        # custom logic, e.g. dismiss a modal first
        page.locator(".modal-close").click() if page.locator(".modal").count() else None
        return click(page, text, **kwargs)

    OVERRIDES = {
        "click": _my_click,
    }

RESOLUTION ORDER
─────────────────
    1. Override function for the step's module   (if found)
    2. Generic function from actions.py          (fallback)

The active module for a test case is:
    • The `module` field in the YAML/Excel test case row (explicit)
    • OR the first segment of page.url() path at the time of the step (auto)
    • OR None → always use the generic function
"""

import importlib
import os
import re

_registry: dict[str, dict] = {}


def load_all() -> None:
    """Import every override module in this package directory."""
    here = os.path.dirname(__file__)
    for fname in sorted(os.listdir(here)):
        if not fname.endswith(".py") or fname == "__init__.py":
            continue
        mod_id = fname[:-3]
        try:
            mod = importlib.import_module(f"overrides.{mod_id}")
        except Exception as exc:
            print(f"  [overrides] WARNING: could not load '{fname}': {exc}")
            continue
        name      = getattr(mod, "MODULE_NAME", None)
        overrides = getattr(mod, "OVERRIDES", None)
        if name and isinstance(overrides, dict):
            _registry[name] = overrides
            print(f"  [overrides] loaded '{name}' "
                  f"({len(overrides)} override(s): {', '.join(overrides)})")


def get_function(module_name: str | None, function_name: str, default_fn):
    """
    Return the override for (module_name, function_name) if one is registered,
    otherwise return default_fn.
    """
    if module_name and module_name in _registry:
        fn = _registry[module_name].get(function_name)
        if fn:
            return fn
    return default_fn


def detect_module_from_url(url: str) -> str | None:
    """
    Auto-detect the module name from the first non-empty URL path segment.
    E.g. 'https://app.example.com/dashboard/reports' → 'dashboard'
    """
    try:
        path = re.sub(r"https?://[^/]+", "", url)  # strip scheme + host
        segments = [s for s in path.split("/") if s]
        return segments[0] if segments else None
    except Exception:
        return None
