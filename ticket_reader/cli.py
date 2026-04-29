"""Command-line interface for ticket-reader."""

import argparse
import csv
import dataclasses
import json
import sys
from pathlib import Path

from . import __version__, read
from .models import Ticket

# Maximum display width per column: ticket#, description, status, owner, type
_MAX_WIDTHS = (None, 50, 35, 20, 12)


def _truncate(s: str, max_len: int | None) -> str:
    if max_len is None or len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def _print_table(tickets: list[Ticket]) -> None:
    headers = ["Ticket #", "Description", "Status", "Owner", "Type"]
    rows = [
        [t.ticket_number, t.description, t.status, t.owner, t.issue_type]
        for t in tickets
    ]

    widths = [
        max(len(h), max((len(r[i]) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    for i, cap in enumerate(_MAX_WIDTHS):
        if cap is not None:
            widths[i] = min(widths[i], cap)

    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)

    print(fmt.format(*headers))
    print(sep)
    for row in rows:
        truncated = [_truncate(str(v), _MAX_WIDTHS[i]) for i, v in enumerate(row)]
        print(fmt.format(*truncated))


def _print_csv(tickets: list[Ticket]) -> None:
    if not tickets:
        return
    fields = [f.name for f in dataclasses.fields(tickets[0])]
    writer = csv.DictWriter(sys.stdout, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for t in tickets:
        writer.writerow(dataclasses.asdict(t))


def _print_json(tickets: list[Ticket]) -> None:
    print(json.dumps([dataclasses.asdict(t) for t in tickets], indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ticket-reader",
        description="Read and display tickets from CSV or XLSX files.",
    )
    parser.add_argument("filepath", help="Path to the ticket file (.csv or .xlsx)")
    parser.add_argument(
        "--format",
        choices=["table", "csv", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()

    try:
        tickets = read(args.filepath)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not tickets:
        print("No tickets found.")
        return

    if args.format == "json":
        _print_json(tickets)
    elif args.format == "csv":
        _print_csv(tickets)
    else:
        _print_table(tickets)
