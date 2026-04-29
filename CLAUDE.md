# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Python 3.13.7. Always activate the venv before running anything:

```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# Bash (Git Bash / WSL)
source venv/Scripts/activate
```

## Common commands

```bash
# Install the package in editable mode with dev deps (first-time setup)
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_csv_reader.py -v

# Run the CLI against local data files
ticket-reader Tickets.csv
ticket-reader Tickets.xlsx --format json
```

## Package structure

```
ticket_reader/
  __init__.py      # public API: read(), read_csv(), read_xlsx(), Ticket, __version__
  models.py        # Ticket dataclass
  csv_reader.py    # read_csv() — headers on row 1
  xlsx_reader.py   # read_xlsx() — headers on row 2, data from row 3
  cli.py           # argparse entry point registered as `ticket-reader`
tests/
  conftest.py      # pytest fixtures that build XLSX files via openpyxl
  fixtures/        # CSV fixture files (sample.csv, sample_with_blanks.csv, no_ticket_col.csv)
  test_csv_reader.py
  test_xlsx_reader.py
```

## Key design notes

- **Column matching** in both readers: headers are normalized via `.strip().lower()` before lookup, so `" Status"` and `"status"` both resolve correctly. The CSV in this repo has a leading space on the `Status` header.
- **XLSX header row** is always row 2 (not row 1). Row 1 is skipped as a title row. This is hardcoded in `xlsx_reader.py:ws[2]` and `iter_rows(min_row=3)`.
- **Blank / repeated-header rows** mid-file are skipped by checking whether the ticket number cell is empty or equals `"ticket number"` (case-insensitive).
- The `read()` auto-dispatch in `__init__.py` routes on file extension (`.csv` → `read_csv`, `.xlsx` → `read_xlsx`). Only these two extensions are supported.

## Publishing checklist

1. Update `Repository` and `Issues` URLs in `pyproject.toml`.
2. Bump `version` in both `pyproject.toml` and `ticket_reader/__init__.py`.
3. `git init && git add . && git commit -m "initial release"`
4. Push to GitHub. Users can then install with `pip install git+https://github.com/you/ticket-reader.git`.
5. To publish to PyPI: `pip install build twine && python -m build && twine upload dist/*`.
