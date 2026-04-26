"""
reporter.py — Records step-level results and writes CSV, JSON, and Excel output.

Files written to the output/ directory:

  output/<name>_summary.csv    — one row per test case
  output/<name>_details.csv    — one row per step
  output/<name>_results.json   — full structured results (for CI / dashboards)
  output/<name>_results.xlsx   — Excel workbook with Summary + Details sheets

Usage
─────
    reporter = TestReporter()
    reporter.start_test("TC-001", "Login flow", module="auth")
    reporter.execute("Go to app", lambda: go_to(page, APP_URL))
    reporter.execute("Click login", lambda: click(page, "Login"))
    reporter.end_test()
    reporter.to_files("output/my_run")
"""

import csv
import json
import os
import time
from datetime import datetime

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


class TestReporter:
    def __init__(self):
        self._results: list[dict] = []
        self._current: dict | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start_test(self, tc_id: str, scenario: str, *, module: str = None) -> None:
        self._current = {
            "id":       tc_id,
            "scenario": scenario,
            "module":   module or "",
            "steps":    [],
            "status":   "PASS",
            "error":    "",
            "start":    time.time(),
        }

    def end_test(self) -> None:
        if self._current:
            self._current["duration_s"] = round(time.time() - self._current["start"], 2)
            self._results.append(self._current)
            self._current = None

    # ── Step execution ────────────────────────────────────────────────────────

    def execute(self, description: str, action, *, stop_on_fail: bool = False) -> bool:
        """
        Run one step, log its result, return True/False.
        If stop_on_fail is True and the step fails, re-raise the exception.
        """
        if not self._current:
            raise RuntimeError("Call start_test() before execute()")
        step_start = time.time()
        try:
            result = action()
            if result is False:
                raise AssertionError("Action returned False")
            self._log_step(description, "PASS", "", round(time.time() - step_start, 2))
            return True
        except Exception as exc:
            err = str(exc)
            self._log_step(description, "FAIL", err, round(time.time() - step_start, 2))
            if not self._current["error"]:
                self._current["status"] = "FAIL"
                self._current["error"]  = err
            if stop_on_fail:
                raise
            return False

    def run_steps(self, steps: list[tuple], *, stop_on_fail: bool = False) -> bool:
        """
        Execute a static list of (description, callable) pairs.
        Calls end_test() automatically. Returns True only if all steps passed.
        """
        if not self._current:
            raise RuntimeError("Call start_test() before run_steps()")
        all_ok = True
        try:
            for description, action in steps:
                ok = self.execute(description, action, stop_on_fail=stop_on_fail)
                if not ok:
                    all_ok = False
        finally:
            self.end_test()
        return all_ok

    # ── Internal ──────────────────────────────────────────────────────────────

    def _log_step(self, description: str, status: str, error: str,
                  duration_s: float) -> None:
        self._current["steps"].append({
            "step":        len(self._current["steps"]) + 1,
            "description": description,
            "status":      status,
            "error":       error,
            "duration_s":  duration_s,
        })

    # ── Output ────────────────────────────────────────────────────────────────

    def to_files(self, base_path: str = "output/test_results") -> tuple[str, str, str]:
        """
        Write summary CSV, details CSV, and JSON.
        Returns (summary_path, details_path, json_path).
        """
        os.makedirs(os.path.dirname(base_path) or ".", exist_ok=True)

        summary_path = f"{base_path}_summary.csv"
        details_path = f"{base_path}_details.csv"
        json_path    = f"{base_path}_results.json"

        # ── Summary CSV ───────────────────────────────────────────────────────
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["TC ID", "Scenario", "Module", "Total Steps",
                        "Passed", "Failed", "Status", "Duration (s)", "Error"])
            for tc in self._results:
                steps  = tc["steps"]
                passed = sum(1 for s in steps if s["status"] == "PASS")
                w.writerow([
                    tc["id"], tc["scenario"], tc["module"],
                    len(steps), passed, len(steps) - passed,
                    tc["status"], tc.get("duration_s", ""), tc["error"],
                ])

        # ── Details CSV ───────────────────────────────────────────────────────
        with open(details_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["TC ID", "Scenario", "Step #", "Description",
                        "Status", "Duration (s)", "Error"])
            for tc in self._results:
                for s in tc["steps"]:
                    w.writerow([
                        tc["id"], tc["scenario"], s["step"],
                        s["description"], s["status"], s["duration_s"], s["error"],
                    ])

        # ── JSON ──────────────────────────────────────────────────────────────
        summary = {
            "run_date":   datetime.now().isoformat(timespec="seconds"),
            "total":      len(self._results),
            "passed":     sum(1 for tc in self._results if tc["status"] == "PASS"),
            "failed":     sum(1 for tc in self._results if tc["status"] == "FAIL"),
            "test_cases": self._results,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # ── Excel ─────────────────────────────────────────────────────────────
        xlsx_path = _write_results_xlsx(self._results, base_path, summary)

        print(f"\n{'='*60}")
        print(f"  RESULTS: {summary['passed']} passed, {summary['failed']} failed "
              f"of {summary['total']} test case(s)")
        print(f"{'='*60}")
        print(f"  Summary → {summary_path}")
        print(f"  Details → {details_path}")
        print(f"  JSON    → {json_path}")
        print(f"  Excel   → {xlsx_path}")
        return summary_path, details_path, json_path

    # ── Legacy compat (used by original test_cases.py) ───────────────────────

    def log_step(self, description: str, result: str = "PASS",
                 error: str = "") -> None:
        self._log_step(description, result, error, 0)
        if result == "FAIL" and self._current and not self._current["error"]:
            self._current["status"] = "FAIL"
            self._current["error"]  = error

    def to_csv(self, base_path: str = "test_results") -> tuple[str, str]:
        """Legacy alias — writes to output/ dir, returns (summary, details)."""
        if not base_path.startswith("output"):
            base_path = f"output/{base_path}"
        s, d, _ = self.to_files(base_path)
        return s, d


# ── Excel writer (module-level, shared with sample generator) ─────────────────

# Palette
_C_HEADER  = "2E4057"   # dark blue  — column headers
_C_PASS    = "D6EFD8"   # light green
_C_FAIL    = "FDDEDE"   # light red
_C_ALT     = "F5F8FB"   # light grey — alternating rows
_C_TITLE   = "1A2E42"   # darker blue — sheet title row


def _hdr_style(cell, bg: str = _C_HEADER) -> None:
    cell.font      = Font(bold=True, color="FFFFFF", size=10)
    cell.fill      = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="center", vertical="center",
                                wrap_text=True)


def _data_style(cell, bg: str = None, bold: bool = False,
                wrap: bool = False, center: bool = False) -> None:
    cell.font      = Font(bold=bold, size=10)
    cell.alignment = Alignment(vertical="top", wrap_text=wrap,
                                horizontal="center" if center else "left")
    if bg:
        cell.fill = PatternFill("solid", fgColor=bg)


def _status_color(status: str) -> str:
    return _C_PASS if status == "PASS" else _C_FAIL


def _set_col_widths(ws, widths: list[int]) -> None:
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _write_results_xlsx(results: list[dict], base_path: str,
                        summary: dict) -> str:
    """Write a formatted Excel workbook and return the file path."""
    xlsx_path = f"{base_path}_results.xlsx"
    wb = openpyxl.Workbook()

    # ── Sheet 1: Summary ──────────────────────────────────────────────────────
    ws_sum = wb.active
    ws_sum.title = "Summary"

    # Title row
    ws_sum.merge_cells("A1:I1")
    title_cell = ws_sum["A1"]
    title_cell.value     = (f"Test Run Results  —  {summary['run_date']}  |  "
                             f"{summary['passed']} passed, {summary['failed']} failed"
                             f"  of {summary['total']}")
    title_cell.font      = Font(bold=True, color="FFFFFF", size=12)
    title_cell.fill      = PatternFill("solid", fgColor=_C_TITLE)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_sum.row_dimensions[1].height = 28

    # Header row
    sum_headers = ["TC ID", "Scenario", "Module", "Total Steps",
                   "Passed", "Failed", "Status", "Duration (s)", "Error"]
    for col, h in enumerate(sum_headers, start=1):
        _hdr_style(ws_sum.cell(row=2, column=col, value=h))
    ws_sum.row_dimensions[2].height = 22
    ws_sum.freeze_panes = "A3"

    # Data rows
    for r, tc in enumerate(results, start=3):
        steps  = tc["steps"]
        passed = sum(1 for s in steps if s["status"] == "PASS")
        failed = len(steps) - passed
        bg     = _C_ALT if r % 2 == 0 else None
        status_bg = _status_color(tc["status"])

        row_vals = [
            tc["id"], tc["scenario"], tc.get("module", ""),
            len(steps), passed, failed,
            tc["status"], tc.get("duration_s", ""), tc["error"],
        ]
        for col, val in enumerate(row_vals, start=1):
            cell_bg = status_bg if col == 7 else bg
            cell = ws_sum.cell(row=r, column=col, value=val)
            _data_style(cell, bg=cell_bg, bold=(col == 1), center=(col in (4, 5, 6, 7, 8)))

    _set_col_widths(ws_sum, [10, 38, 12, 11, 9, 9, 10, 12, 40])

    # ── Sheet 2: Details ──────────────────────────────────────────────────────
    ws_det = wb.create_sheet("Details")

    det_headers = ["TC ID", "Scenario", "Module", "Step #",
                   "Description", "Function", "Status", "Duration (s)", "Error"]
    for col, h in enumerate(det_headers, start=1):
        _hdr_style(ws_det.cell(row=1, column=col, value=h))
    ws_det.row_dimensions[1].height = 22
    ws_det.freeze_panes = "A2"

    row_num = 2
    for tc in results:
        for s in tc["steps"]:
            bg        = _C_ALT if row_num % 2 == 0 else None
            status_bg = _status_color(s["status"])
            # parse function name from description fallback
            fn_name   = s.get("function", "")
            row_vals  = [
                tc["id"], tc["scenario"], tc.get("module", ""),
                s["step"], s["description"], fn_name,
                s["status"], s["duration_s"], s["error"],
            ]
            for col, val in enumerate(row_vals, start=1):
                cell_bg = status_bg if col == 7 else bg
                cell = ws_det.cell(row=row_num, column=col, value=val)
                _data_style(cell, bg=cell_bg, bold=(col == 1),
                            center=(col in (4, 7, 8)), wrap=(col == 5))
            row_num += 1

    _set_col_widths(ws_det, [10, 30, 10, 8, 44, 18, 10, 12, 38])

    wb.save(xlsx_path)
    return xlsx_path
