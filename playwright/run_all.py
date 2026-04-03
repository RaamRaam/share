"""
Orchestrator — runs all test cases in order, then generates the CSV reports.

Usage:
    python run_all.py                       # run all tests
    python run_all.py --stop-on-fail        # stop at first failure
    python run_all.py --report my_results   # custom report base name
"""

import sys
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright

from config import CHROME_USER_DATA_DIR, CHROME_PROFILE, BROWSER_ARGS, HEADLESS, SLOW_MO
from reporter import TestReporter
from test_cases import TEST_CASES


def parse_args():
    parser = argparse.ArgumentParser(description="Playwright test runner")
    parser.add_argument("--stop-on-fail", action="store_true",
                        help="Stop execution after the first failing test case")
    parser.add_argument("--report", default="", metavar="NAME",
                        help="Output base name (default: test_results_<timestamp>)")
    return parser.parse_args()


def run_all(stop_on_fail: bool = False, report_path: str = "") -> None:
    reporter = TestReporter()

    if not report_path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"test_results_{ts}"

    print(f"\n{'='*60}")
    print(f"  Playwright Test Runner  —  {len(TEST_CASES)} test case(s)")
    print(f"{'='*60}\n")

    # Use .start() instead of context manager so the browser stays open after tests finish
    pw      = sync_playwright().start()
    context = pw.chromium.launch_persistent_context(
        user_data_dir=CHROME_USER_DATA_DIR,
        channel="msedge",
        args=BROWSER_ARGS,
        headless=HEADLESS,
        slow_mo=SLOW_MO,
    )
    page = context.new_page()
    page.set_default_timeout(0)

    passed = failed = 0

    for tc_fn in TEST_CASES:
        print(f"▶  Running  {tc_fn.__name__} …")
        ok = tc_fn(page, reporter)

        if ok:
            passed += 1
            print(f"   ✅  PASS")
        else:
            failed += 1
            print(f"   ❌  FAIL")
            if stop_on_fail:
                print("\n⛔  --stop-on-fail set — aborting remaining tests.")
                break

    print(f"\n{'='*60}")
    print(f"  Results: {passed} passed, {failed} failed out of {passed + failed} run")
    print(f"{'='*60}")

    summary_path, details_path = reporter.to_csv(report_path)

    # Open both CSV files in VS Code
    import subprocess, os
    subprocess.Popen(["code", os.path.abspath(summary_path)])
    subprocess.Popen(["code", os.path.abspath(details_path)])
    print(f"📊  Opening reports in VS Code → {summary_path}  |  {details_path}")

    # Keep the script (and browser) alive until the user decides to close
    print("\n🌐  Browser is still open. Press ENTER here to close it.")
    input()

    context.close()
    pw.stop()

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    run_all(stop_on_fail=args.stop_on_fail, report_path=args.report)
