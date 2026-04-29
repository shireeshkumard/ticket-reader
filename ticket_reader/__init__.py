"""ticket-reader: Read and parse support tickets from CSV and XLSX files."""

from pathlib import Path

from .csv_reader import read_csv
from .models import Ticket
from .xlsx_reader import read_xlsx

__version__ = "0.1.0"
__all__ = ["Ticket", "read", "read_csv", "read_xlsx", "__version__"]


def read(filepath: str | Path) -> list[Ticket]:
    """Auto-detect file format and read tickets.

    Dispatches to :func:`read_csv` or :func:`read_xlsx` based on the file
    extension (``.csv`` or ``.xlsx``).

    Args:
        filepath: Path to a ``.csv`` or ``.xlsx`` ticket file.

    Returns:
        List of :class:`Ticket` objects.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the extension is unsupported or a required column
            is missing.

    Example::

        from ticket_reader import read

        tickets = read("Tickets.xlsx")
        blockers = [t for t in tickets if t.issue_type == "Blocker"]
    """
    p = Path(filepath)
    ext = p.suffix.lower()
    if ext == ".csv":
        return read_csv(p)
    elif ext == ".xlsx":
        return read_xlsx(p)
    else:
        raise ValueError(
            f"Unsupported file extension '{ext}'. Supported formats: .csv, .xlsx"
        )
