"""
excel_to_yaml.py — Convert a test-cases Excel workbook to a YAML file.

Excel format (one row per step)
────────────────────────────────
  Column A  Test Case ID      TC001
  Column B  Test Scenario     Login Flow
  Column C  Step Number       1
  Column D  Step Function     go_to
  Column E  Step Parameters   {"url": "${APP_URL}"}
  Column F  Module            auth          (optional — drives override lookup)
  Column G  Step Description  Go to app     (optional — used in reports)
  Column H  Expected Result   /home         (optional — stored for reference)

Parameters column must contain valid JSON (or be empty).
Use ${VAR_NAME} in parameter values to reference environment variables.
Multiple rows with the same TC ID are grouped into one test case.

Usage
─────
  python excel_to_yaml.py                           # default paths
  python excel_to_yaml.py tests/my.xlsx tests/my.yaml
  python excel_to_yaml.py --excel tests/my.xlsx --yaml tests/my.yaml
"""

import argparse
import json
import sys
from pathlib import Path

import openpyxl
import yaml


# ── Column index map (1-based per openpyxl) ──────────────────────────────────
COL = {
    "tc_id":       1,
    "scenario":    2,
    "step":        3,
    "function":    4,
    "params":      5,
    "module":      6,
    "description": 7,
    "expected":    8,
}

HEADER_ROWS = 1   # number of header rows to skip


def _cell(row, col: int):
    """Return stripped string value of a cell, or empty string."""
    val = row[col - 1].value
    return str(val).strip() if val is not None else ""


def _parse_params(raw: str) -> dict:
    """
    Parse the Step Parameters cell.
    Accepts JSON objects or empty string (returns {}).
    Raises ValueError with a helpful message on malformed JSON.
    """
    raw = raw.strip()
    if not raw:
        return {}
    try:
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError("Parameters must be a JSON object {}, not a list or scalar")
        return result
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in Step Parameters: {raw!r}\n  Error: {exc}"
        ) from exc


def excel_to_yaml(excel_path: str | Path,
                  yaml_path: str | Path,
                  sheet_name: str = None) -> dict:
    """
    Read `excel_path`, convert to YAML structure, write to `yaml_path`.
    Returns the parsed dict (useful for tests / programmatic use).
    """
    excel_path = Path(excel_path)
    yaml_path  = Path(yaml_path)

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active
    print(f"  Reading sheet '{ws.title}' from {excel_path.name} …")

    test_cases_map: dict[str, dict] = {}  # keyed by tc_id
    errors: list[str] = []

    for row_num, row in enumerate(ws.iter_rows(), start=1):
        if row_num <= HEADER_ROWS:
            continue
        if all(c.value is None for c in row):
            continue  # skip blank rows

        tc_id       = _cell(row, COL["tc_id"])
        scenario    = _cell(row, COL["scenario"])
        step_num    = _cell(row, COL["step"])
        function    = _cell(row, COL["function"])
        params_raw  = _cell(row, COL["params"])
        module      = _cell(row, COL["module"])
        description = _cell(row, COL["description"])
        expected    = _cell(row, COL["expected"])

        if not tc_id or not function:
            continue   # sparse row without required fields

        try:
            params = _parse_params(params_raw)
        except ValueError as exc:
            errors.append(f"Row {row_num} ({tc_id} step {step_num}): {exc}")
            continue

        step_entry = {
            "step":     int(step_num) if step_num.isdigit() else row_num,
            "function": function,
        }
        if params:
            step_entry["params"] = params
        if description:
            step_entry["description"] = description
        if expected:
            step_entry["expected"] = expected

        if tc_id not in test_cases_map:
            test_cases_map[tc_id] = {
                "id":       tc_id,
                "scenario": scenario or tc_id,
                "module":   module or None,
                "steps":    [],
            }
        else:
            # Update scenario / module if a later row fills them in
            if scenario and not test_cases_map[tc_id]["scenario"]:
                test_cases_map[tc_id]["scenario"] = scenario
            if module and not test_cases_map[tc_id]["module"]:
                test_cases_map[tc_id]["module"] = module

        test_cases_map[tc_id]["steps"].append(step_entry)

    if errors:
        print("\n  ⚠  Parameter parse errors (rows skipped):")
        for e in errors:
            print(f"     {e}")

    # Sort test cases by ID, steps by step number
    test_cases = sorted(test_cases_map.values(), key=lambda tc: tc["id"])
    for tc in test_cases:
        tc["steps"].sort(key=lambda s: s["step"])
        if tc["module"] is None:
            del tc["module"]   # omit if not set

    output = {
        "metadata": {
            "source":  str(excel_path.name),
            "sheet":   ws.title,
            "total":   len(test_cases),
        },
        "test_cases": test_cases,
    }

    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, sort_keys=False,
                  default_flow_style=False)

    print(f"  ✓ Converted {len(test_cases)} test case(s) → {yaml_path}")
    return output


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args():
    p = argparse.ArgumentParser(
        description="Convert a Playwright test-cases Excel file to YAML."
    )
    p.add_argument("excel", nargs="?", default="tests/test_cases.xlsx",
                   help="Input Excel file (default: tests/test_cases.xlsx)")
    p.add_argument("yaml",  nargs="?", default="tests/test_cases.yaml",
                   help="Output YAML file (default: tests/test_cases.yaml)")
    p.add_argument("--excel", dest="excel_opt", metavar="FILE",
                   help="Input Excel file (alternative flag form)")
    p.add_argument("--yaml",  dest="yaml_opt",  metavar="FILE",
                   help="Output YAML file (alternative flag form)")
    p.add_argument("--sheet", default=None,
                   help="Sheet name to read (default: first sheet)")
    return p.parse_args()


if __name__ == "__main__":
    args    = _parse_args()
    e_path  = args.excel_opt or args.excel
    y_path  = args.yaml_opt  or args.yaml
    try:
        excel_to_yaml(e_path, y_path, sheet_name=args.sheet)
    except FileNotFoundError as exc:
        print(f"\n  ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
