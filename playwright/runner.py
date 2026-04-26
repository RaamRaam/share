"""
yaml_runner.py — Main entry point for the Excel-driven Playwright test runner.

Flow
─────
  1. Read CLI args
  2. Convert Excel → YAML  (or load existing YAML if --yaml-only)
  3. Launch browser (persistent Edge/Chrome context, stays open after tests)
  4. Load overrides from overrides/ directory
  5. For each test case: execute each step, resolving overrides per module
  6. Write output reports to output/
  7. Keep browser open — show mouse demo movement — wait for user

Usage
─────
  python yaml_runner.py                              # uses defaults
  python yaml_runner.py --excel tests/my.xlsx
  python yaml_runner.py --yaml tests/my.yaml        # skip Excel conversion
  python yaml_runner.py --tc TC001 TC003            # run specific test cases
  python yaml_runner.py --stop-on-fail
  python yaml_runner.py --report my_run_name

Environment variables (from .env)
───────────────────────────────────
  APP_URL    — application base URL
  SSO_EMAIL  — SSO user email
  Any ${VAR} in step params is substituted from os.environ at runtime.
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

import actions
import overrides
from config import (
    CHROME_USER_DATA_DIR, BROWSER_ARGS,
    HEADLESS, SLOW_MO, APP_URL,
)
from excel_to_yaml import excel_to_yaml
from reporter import TestReporter

load_dotenv()


# ── Function registry ─────────────────────────────────────────────────────────
# Maps YAML step_function strings to actual callables from actions.py.
# Add entries here whenever you add a new action function.

FUNCTION_MAP: dict[str, callable] = {
    # Navigation
    "go_to":            actions.go_to,
    "wait_for_page":    actions.wait_for_page,
    "wait_for_url":     actions.wait_for_url,
    "check_url":        actions.check_url,
    # Clicking
    "click":            actions.click,
    "click_element":    actions.click_element,
    "click_all":        actions.click_all,
    "click_checkbox":   actions.click_checkbox,
    # Forms
    "fill_input":       actions.fill_input,
    "fill_all":         actions.fill_all,
    "clear_input":      actions.clear_input,
    "select_dropdown":  actions.select_dropdown,
    "multi_select":     actions.multi_select,
    # Search / combo
    "search_input":     actions.search_input,
    # Reading
    "get_text":         actions.get_text,
    "get_adjacent_text":actions.get_adjacent_text,
    "get_attribute":    actions.get_attribute,
    # Table
    "get_row_text":     actions.get_row_text,
    "click_row_icon":   actions.click_row_icon,
    # Verification
    "check_visible":    actions.check_visible,
    "check_text":       actions.check_text,
    "check_title":      actions.check_title,
    "check_count":      actions.check_count,
    # Waiting
    "wait_for":         actions.wait_for,
    # Demo
    "demo_mouse_move":  actions.demo_mouse_move,
}


# ── Variable substitution ─────────────────────────────────────────────────────

def _substitute(value, env: dict):
    """Replace ${VAR} tokens with environment variable values (recursive)."""
    if isinstance(value, str):
        return re.sub(
            r"\$\{(\w+)\}",
            lambda m: env.get(m.group(1), os.environ.get(m.group(1), m.group(0))),
            value,
        )
    if isinstance(value, dict):
        return {k: _substitute(v, env) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute(v, env) for v in value]
    return value


# ── Step executor ─────────────────────────────────────────────────────────────

def _run_step(page, step: dict, module: str | None,
              reporter: TestReporter, env: dict,
              stop_on_fail: bool) -> bool:
    """
    Resolve the function (with override), substitute vars, execute, and
    record the result via the reporter.
    """
    fn_name = step.get("function", "")
    params  = _substitute(step.get("params", {}), env)
    desc    = step.get("description") or f"{fn_name}({params})"

    default_fn = FUNCTION_MAP.get(fn_name)
    if default_fn is None:
        err = f"Unknown function '{fn_name}' — add it to FUNCTION_MAP in yaml_runner.py"
        return reporter.execute(desc, lambda: (_ for _ in ()).throw(ValueError(err)),
                                stop_on_fail=stop_on_fail)

    # Auto-detect module from URL if not explicitly set
    active_module = module or overrides.detect_module_from_url(page.url)
    fn = overrides.get_function(active_module, fn_name, default_fn)

    return reporter.execute(
        desc,
        lambda fn=fn, params=params: fn(page, **params),
        stop_on_fail=stop_on_fail,
    )


# ── Test case runner ──────────────────────────────────────────────────────────

def run_yaml(yaml_path: str | Path, page, reporter: TestReporter,
             *, tc_filter: list[str] = None,
             stop_on_fail: bool = False) -> tuple[int, int]:
    """
    Load YAML, execute every test case (or only those in tc_filter),
    return (passed, failed).
    """
    yaml_path = Path(yaml_path)
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    test_cases = data.get("test_cases", [])
    if tc_filter:
        test_cases = [tc for tc in test_cases if tc["id"] in tc_filter]
        if not test_cases:
            print(f"\n  ⚠  No test cases found matching: {tc_filter}")

    env = dict(os.environ)

    passed = failed = 0
    for tc in test_cases:
        tc_id    = tc["id"]
        scenario = tc.get("scenario", tc_id)
        module   = tc.get("module")

        print(f"\n▶  {tc_id}: {scenario}", end="")
        if module:
            print(f"  [module={module}]", end="")
        print()

        reporter.start_test(tc_id, scenario, module=module)
        tc_ok = True

        for step in tc.get("steps", []):
            ok = _run_step(page, step, module, reporter, env, stop_on_fail)
            if not ok:
                tc_ok = False
                if stop_on_fail:
                    break

        reporter.end_test()

        if tc_ok:
            passed += 1
            print(f"   ✅  PASS")
        else:
            failed += 1
            print(f"   ❌  FAIL")
            if stop_on_fail:
                print("\n⛔  --stop-on-fail set — aborting.")
                break

    return passed, failed


# ── Browser launch ────────────────────────────────────────────────────────────

def _launch_browser(pw):
    return pw.chromium.launch_persistent_context(
        user_data_dir=CHROME_USER_DATA_DIR,
        channel="msedge",
        args=BROWSER_ARGS,
        headless=HEADLESS,
        no_viewport=True,
        slow_mo=SLOW_MO,
    )


# ── Demo: sweep mouse after all tests ────────────────────────────────────────

def _demo_sweep(page) -> None:
    print("\n🖱  Sweeping mouse to show automation completed …")
    try:
        actions.demo_mouse_move(page, steps=20, duration_ms=2_000)
    except Exception:
        pass


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args():
    p = argparse.ArgumentParser(
        description="Run Playwright tests from an Excel file via YAML."
    )
    p.add_argument("--excel",       default="tests/test_cases.xlsx",
                   help="Input Excel file  (default: tests/test_cases.xlsx)")
    p.add_argument("--yaml",        default="tests/test_cases.yaml",
                   help="YAML file path    (default: tests/test_cases.yaml)")
    p.add_argument("--yaml-only",   action="store_true",
                   help="Skip Excel conversion, load YAML directly")
    p.add_argument("--sheet",       default=None,
                   help="Excel sheet name  (default: first sheet)")
    p.add_argument("--tc",          nargs="+", metavar="TC_ID",
                   help="Run only these test case IDs  e.g. --tc TC001 TC003")
    p.add_argument("--stop-on-fail",action="store_true",
                   help="Stop after first failed step")
    p.add_argument("--report",      default="",
                   help="Output base name  (default: auto-timestamped)")
    return p.parse_args()


def main():
    args = _parse_args()

    # ── Step 1: Excel → YAML ─────────────────────────────────────────────────
    if not args.yaml_only:
        print(f"\n{'='*60}")
        print(f"  Converting Excel → YAML")
        print(f"{'='*60}")
        excel_to_yaml(args.excel, args.yaml, sheet_name=args.sheet)
    else:
        yaml_path = Path(args.yaml)
        if not yaml_path.exists():
            print(f"ERROR: YAML file not found: {yaml_path}", file=sys.stderr)
            sys.exit(1)
        print(f"\n  Loading YAML from {yaml_path} (--yaml-only)")

    # ── Step 2: Count test cases ─────────────────────────────────────────────
    with open(args.yaml, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    total = len(data.get("test_cases", []))
    print(f"\n{'='*60}")
    print(f"  Playwright YAML Test Runner — {total} test case(s)")
    print(f"{'='*60}")

    # ── Step 3: Load overrides ────────────────────────────────────────────────
    print("\n  Loading overrides …")
    overrides.load_all()

    # ── Step 4: Launch browser ────────────────────────────────────────────────
    pw      = sync_playwright().start()
    context = _launch_browser(pw)
    page    = context.new_page()
    page.set_default_timeout(0)

    if APP_URL:
        print(f"\n  Opening {APP_URL} …")
        page.goto(APP_URL, wait_until="networkidle")

    # ── Step 5: Run tests ─────────────────────────────────────────────────────
    reporter = TestReporter()
    passed, failed = run_yaml(
        args.yaml, page, reporter,
        tc_filter=args.tc,
        stop_on_fail=args.stop_on_fail,
    )

    # ── Step 6: Write reports ─────────────────────────────────────────────────
    ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name   = args.report or f"run_{ts}"
    report_base = f"output/{base_name}"
    reporter.to_files(report_base)

    # Open reports in VS Code
    import subprocess
    for path in [f"{report_base}_summary.csv",
                 f"{report_base}_details.csv",
                 f"{report_base}_results.json"]:
        if os.path.exists(path):
            subprocess.Popen(["code", os.path.abspath(path)])

    # ── Step 7: Demo sweep + keep browser open ────────────────────────────────
    _demo_sweep(page)

    print("\n🌐  Browser is still open.")
    print("    Press ENTER here to close it (or close it manually).")
    input()

    context.close()
    pw.stop()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
