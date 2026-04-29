# ticket-reader

A Python library and CLI for reading support tickets from CSV and Excel (`.xlsx`) files into typed Python objects.

## Install

```bash
# From GitHub
pip install git+https://github.com/yourusername/ticket-reader.git

# From a local clone
pip install .
```

## Quick start

```python
from ticket_reader import read

tickets = read("Tickets.xlsx")
for t in tickets:
    print(t.ticket_number, t.issue_type, t.status)
```

## Library API

### `read(filepath)` — auto-detect format

Dispatches to `read_csv` or `read_xlsx` based on file extension.

```python
from ticket_reader import read

tickets = read("Tickets.csv")    # or .xlsx — same return type either way
blockers = [t for t in tickets if t.issue_type == "Blocker"]
```

### `read_csv(filepath)` and `read_xlsx(filepath)`

Use these directly when you know the format:

```python
from ticket_reader import read_csv, read_xlsx

csv_tickets  = read_csv("Tickets.csv")
xlsx_tickets = read_xlsx("Tickets.xlsx")
```

All three functions accept a `str` or `pathlib.Path` and return `list[Ticket]`.

### `Ticket` dataclass

```python
from dataclasses import dataclass

@dataclass
class Ticket:
    ticket_number: str   # e.g. "TSR-1176901"
    description:   str
    status:        str
    owner:         str
    issue_type:    str   # e.g. "Blocker", "Critical"
```

Convert to a plain dict or JSON:

```python
import dataclasses, json

d    = dataclasses.asdict(ticket)          # dict
blob = json.dumps(dataclasses.asdict(ticket))  # JSON string
```

Filter, sort, or group with standard Python:

```python
from ticket_reader import read

tickets = read("Tickets.xlsx")

# Filter by owner
pacs = [t for t in tickets if t.owner == "PACS team"]

# Group by issue type
from itertools import groupby
by_type = {k: list(v) for k, v in groupby(sorted(tickets, key=lambda t: t.issue_type), key=lambda t: t.issue_type)}
```

### Errors

| Exception | Cause |
|---|---|
| `FileNotFoundError` | File path does not exist |
| `ValueError` | Unsupported extension, or no `Ticket number` column found |

## CLI

```bash
# Table output (default)
ticket-reader Tickets.csv
ticket-reader Tickets.xlsx

# JSON — useful for scripting or piping to jq
ticket-reader Tickets.xlsx --format json
ticket-reader Tickets.xlsx --format json | jq '.[] | select(.issue_type == "Blocker")'

# CSV — pipe-friendly, preserves all fields
ticket-reader Tickets.csv --format csv

# Version
ticket-reader --version
```

### Table output example

```
Ticket #        | Description                                        | Status                              | Owner                | Type
----------------+----------------------------------------------------+-------------------------------------+----------------------+------------
TSR-1176901     | Questionnaire navigatation forced logout issue     | PACS Provided the workaround is ... | PACS team            | Blocker
TSR-1176124     | Android Crash issues when click the datePicker ... | Waiting for the fix from Product... | Product              | Blocker
```

## Data format

### CSV

Standard CSV, headers on **row 1**.

| Column | Required | Notes |
|---|---|---|
| `Ticket number` | Yes | |
| `Ticket description` | No | |
| `Status` | No | Leading/trailing whitespace in header is fine |
| `Current Owner` | No | |
| `Issue type` | No | |

Column matching is **case-insensitive** and **whitespace-tolerant** — `" Status"` matches `"status"`. Blank rows and repeated header rows mid-file are skipped automatically.

### XLSX

Excel file with headers on **row 2** (row 1 is treated as a title row). Data rows start on row 3. Same column names and matching rules as CSV.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_csv_reader.py -v
```
