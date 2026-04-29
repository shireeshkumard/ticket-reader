import pytest
from pathlib import Path

from ticket_reader import read_csv, Ticket

FIXTURES = Path(__file__).parent / "fixtures"


def test_returns_ticket_objects():
    tickets = read_csv(FIXTURES / "sample.csv")
    assert all(isinstance(t, Ticket) for t in tickets)


def test_correct_count():
    assert len(read_csv(FIXTURES / "sample.csv")) == 2


def test_ticket_fields():
    t = read_csv(FIXTURES / "sample.csv")[0]
    assert t.ticket_number == "TSR-001"
    assert t.description == "Login fails on mobile"
    assert t.status == "Open"
    assert t.owner == "PACS team"
    assert t.issue_type == "Blocker"


def test_skips_blank_rows():
    tickets = read_csv(FIXTURES / "sample_with_blanks.csv")
    assert len(tickets) == 3
    assert all(t.ticket_number for t in tickets)


def test_skips_repeated_headers():
    tickets = read_csv(FIXTURES / "sample_with_blanks.csv")
    assert not any(t.ticket_number.lower() == "ticket number" for t in tickets)


def test_raises_on_missing_column():
    with pytest.raises(ValueError, match="Ticket number"):
        read_csv(FIXTURES / "no_ticket_col.csv")


def test_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        read_csv("does_not_exist.csv")


def test_accepts_string_path():
    assert len(read_csv(str(FIXTURES / "sample.csv"))) > 0
