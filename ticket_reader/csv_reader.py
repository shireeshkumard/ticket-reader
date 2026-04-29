import csv
from pathlib import Path

from .models import Ticket


def read_csv(filepath: str | Path) -> list[Ticket]:
    """Read tickets from a CSV file.

    Args:
        filepath: Path to the CSV file. Headers are expected on row 1.
            Required column: ``Ticket number``. Optional columns:
            ``Ticket description``, ``Status``, ``Current Owner``, ``Issue type``.
            Column matching is case-insensitive and whitespace-tolerant.

    Returns:
        List of :class:`Ticket` objects. Blank rows and repeated header rows
        mid-file are skipped automatically.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no ``Ticket number`` column is found.

    Example::

        from ticket_reader import read_csv

        for ticket in read_csv("Tickets.csv"):
            print(ticket.ticket_number, ticket.issue_type)
    """
    filepath = Path(filepath)
    tickets: list[Ticket] = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return tickets

        # Normalize: strip whitespace + lowercase → actual CSV key
        cols: dict[str, str] = {
            h.strip().lower(): h for h in reader.fieldnames if h
        }

        ticket_col = cols.get("ticket number")
        if ticket_col is None:
            raise ValueError(
                f"No 'Ticket number' column found in '{filepath}'. "
                f"Available columns: {list(reader.fieldnames)}"
            )

        desc_col = cols.get("ticket description")
        status_col = cols.get("status")
        owner_col = cols.get("current owner")
        type_col = cols.get("issue type")

        def get(row: dict, key: str | None) -> str:
            if key is None:
                return ""
            return (row.get(key) or "").strip()

        for row in reader:
            num = get(row, ticket_col)
            if not num or num.lower() == "ticket number":
                continue

            tickets.append(Ticket(
                ticket_number=num,
                description=get(row, desc_col),
                status=get(row, status_col),
                owner=get(row, owner_col),
                issue_type=get(row, type_col),
            ))

    return tickets
