"""
TestReporter — captures step-level results and writes an Excel report.

Excel output has two sheets:
  • Summary — one row per test case  (TC#, scenario, steps, pass, fail, result, duration, error)
  • Details — one row per step       (TC#, scenario, step#, description, result, error)

Usage
─────
    do = Do(page)
    reporter.start_test("TC-001", "Open app and verify home page")
    steps = [
        do.open(APP_URL),
        do.verify_url(APP_URL),
        do.verify_visible("header", "h1"),
    ]
    return reporter.run_steps(steps)
"""

import time
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ── Styles ───────────────────────────────────────────────────────────────────
_HEADER_FILL = PatternFill("solid", fgColor="2E4057")
_PASS_FILL   = PatternFill("solid", fgColor="C6EFCE")
_FAIL_FILL   = PatternFill("solid", fgColor="FFC7CE")
_ALT_FILL    = PatternFill("solid", fgColor="F2F2F2")
_NO_FILL     = PatternFill()
_HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
_PASS_FONT   = Font(bold=True, color="276221")
_FAIL_FONT   = Font(bold=True, color="9C0006")
_THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)


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
        Use inside a manual try/finally when steps are built at runtime (e.g. TC-007).

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

    # ── Excel export ──────────────────────────────────────────────────────────

    def to_excel(self, path: str = "test_results.xlsx") -> str:
        wb = Workbook()
        self._write_summary_sheet(wb)
        self._write_details_sheet(wb)
        wb.save(path)
        print(f"\n✅  Report saved → {path}")
        return path

    # ── Private ───────────────────────────────────────────────────────────────

    def _write_summary_sheet(self, wb: Workbook) -> None:
        ws = wb.active
        ws.title = "Summary"
        headers    = ["TC #", "Scenario", "Total Steps", "Passed", "Failed",
                      "Result", "Duration (s)", "Error"]
        col_widths = [10, 45, 13, 10, 10, 10, 14, 50]
        self._write_header_row(ws, headers, col_widths)

        for row_idx, tc in enumerate(self._results, start=2):
            steps   = tc["steps"]
            passed  = sum(1 for s in steps if s["result"] == "PASS")
            is_pass = tc["result"] == "PASS"
            values  = [tc["tc_num"], tc["scenario"], len(steps), passed,
                       len(steps) - passed, tc["result"],
                       tc.get("duration", ""), tc["error"]]
            for col_idx, val in enumerate(values, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.border    = _THIN_BORDER
                cell.alignment = Alignment(wrap_text=True, vertical="center")
                if col_idx == 6:
                    cell.fill = _PASS_FILL if is_pass else _FAIL_FILL
                    cell.font = _PASS_FONT if is_pass else _FAIL_FONT
                else:
                    cell.fill = _ALT_FILL if row_idx % 2 == 0 else _NO_FILL

        ws.freeze_panes = "A2"

    def _write_details_sheet(self, wb: Workbook) -> None:
        ws = wb.create_sheet("Details")
        headers    = ["TC #", "Scenario", "Step #", "Step Description", "Result", "Error"]
        col_widths = [10, 40, 8, 60, 10, 50]
        self._write_header_row(ws, headers, col_widths)

        row_idx = 2
        for tc in self._results:
            for step in tc["steps"]:
                is_pass = step["result"] == "PASS"
                values  = [tc["tc_num"], tc["scenario"], step["step_num"],
                           step["description"], step["result"], step["error"]]
                for col_idx, val in enumerate(values, start=1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=val)
                    cell.border    = _THIN_BORDER
                    cell.alignment = Alignment(wrap_text=True, vertical="center")
                    if col_idx == 5:
                        cell.fill = _PASS_FILL if is_pass else _FAIL_FILL
                        cell.font = _PASS_FONT if is_pass else _FAIL_FONT
                    else:
                        cell.fill = _ALT_FILL if row_idx % 2 == 0 else _NO_FILL
                row_idx += 1

        ws.freeze_panes = "A2"

    @staticmethod
    def _write_header_row(ws, headers: list[str], col_widths: list[int]) -> None:
        for col_idx, (hdr, width) in enumerate(zip(headers, col_widths), start=1):
            cell = ws.cell(row=1, column=col_idx, value=hdr)
            cell.font      = _HEADER_FONT
            cell.fill      = _HEADER_FILL
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border    = _THIN_BORDER
            ws.column_dimensions[get_column_letter(col_idx)].width = width
        ws.row_dimensions[1].height = 20
