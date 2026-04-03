"""
TestReporter — captures step-level results and writes CSV reports.

Two CSV files are written:
  • <name>_summary.csv — one row per test case  (TC#, scenario, steps, pass, fail, result, duration, error)
  • <name>_details.csv — one row per step       (TC#, scenario, step#, description, result, error)

Usage
─────
    reporter.start_test("TC-001", "Open app and verify home page")
    steps = [
        ("Go to the application URL",    lambda: go_to(page, APP_URL)),
        ("Verify URL loaded correctly",  lambda: check_url(page, APP_URL)),
    ]
    return reporter.run_steps(steps)
"""

import csv
import time


class TestReporter:
    def __init__(self):
        self._results: list[dict] = []
        self._current: dict | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start_test(self, tc_num: str, scenario: str) -> None:
        self._current = {
            "tc_num":   tc_num,
            "scenario": scenario,
            "steps":    [],
            "result":   "PASS",
            "error":    "",
            "start":    time.time(),
        }

    def end_test(self) -> None:
        if self._current:
            self._current["duration"] = round(time.time() - self._current["start"], 2)
            self._results.append(self._current)
            self._current = None

    # ── Step logging ──────────────────────────────────────────────────────────

    def log_step(self, description: str, result: str = "PASS", error: str = "") -> None:
        if not self._current:
            raise RuntimeError("Call start_test() before log_step()")
        self._current["steps"].append({
            "step_num":    len(self._current["steps"]) + 1,
            "description": description,
            "result":      result,
            "error":       error,
        })
        if result == "FAIL" and not self._current["error"]:
            self._current["result"] = "FAIL"
            self._current["error"]  = error

    # ── Single-step executor (for dynamic TCs) ────────────────────────────────

    def execute(self, description: str, action) -> bool:
        """
        Execute ONE step and log its result immediately.
        Use inside a manual try/finally when steps are built at runtime.

        Returns True on success, False on failure.
        """
        if not self._current:
            raise RuntimeError("Call start_test() before execute()")
        try:
            result = action()
            if result is False:
                raise AssertionError("Action returned False")
            self.log_step(description, "PASS")
            return True
        except Exception as exc:
            self.log_step(description, "FAIL", str(exc))
            return False

    # ── Static step runner (for fixed-step TCs) ───────────────────────────────

    def run_steps(self, steps: list[tuple]) -> bool:
        """
        Execute a fixed list of (description, callable) steps.
        Calls end_test() automatically. Returns True only if all steps passed.
        """
        if not self._current:
            raise RuntimeError("Call start_test() before run_steps()")
        all_passed = True
        try:
            for description, action in steps:
                try:
                    result = action()
                    if result is False:
                        raise AssertionError("Action returned False")
                    self.log_step(description, "PASS")
                except Exception as exc:
                    self.log_step(description, "FAIL", str(exc))
                    all_passed = False
        finally:
            self.end_test()
        return all_passed

    # ── CSV export ────────────────────────────────────────────────────────────

    def to_csv(self, base_path: str = "test_results") -> tuple[str, str]:
        """
        Write two CSV files:
          <base_path>_summary.csv  — one row per test case
          <base_path>_details.csv  — one row per step

        Returns (summary_path, details_path).
        """
        # Strip .csv extension if the caller included it
        if base_path.endswith(".csv"):
            base_path = base_path[:-4]

        summary_path = f"{base_path}_summary.csv"
        details_path = f"{base_path}_details.csv"

        # Summary
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["TC #", "Scenario", "Total Steps", "Passed",
                             "Failed", "Result", "Duration (s)", "Error"])
            for tc in self._results:
                steps  = tc["steps"]
                passed = sum(1 for s in steps if s["result"] == "PASS")
                writer.writerow([
                    tc["tc_num"],
                    tc["scenario"],
                    len(steps),
                    passed,
                    len(steps) - passed,
                    tc["result"],
                    tc.get("duration", ""),
                    tc["error"],
                ])

        # Details
        with open(details_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["TC #", "Scenario", "Step #",
                             "Step Description", "Result", "Error"])
            for tc in self._results:
                for step in tc["steps"]:
                    writer.writerow([
                        tc["tc_num"],
                        tc["scenario"],
                        step["step_num"],
                        step["description"],
                        step["result"],
                        step["error"],
                    ])

        print(f"\n✅  Reports saved:")
        print(f"    Summary → {summary_path}")
        print(f"    Details → {details_path}")
        return summary_path, details_path
