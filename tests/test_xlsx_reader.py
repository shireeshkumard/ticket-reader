import pytest

from ticket_reader import read_xlsx, Ticket


def test_returns_ticket_objects(sample_xlsx):
    assert all(isinstance(t, Ticket) for t in read_xlsx(sample_xlsx))


def test_correct_count(sample_xlsx):
    assert len(read_xlsx(sample_xlsx)) == 2


def test_ticket_fields(sample_xlsx):
    t = read_xlsx(sample_xlsx)[0]
    assert t.ticket_number == "TSR-001"
    assert t.description == "Login fails on mobile"
    assert t.status == "Open"
    assert t.owner == "PACS team"
    assert t.issue_type == "Blocker"


def test_skips_blank_rows(xlsx_with_blanks):
    tickets = read_xlsx(xlsx_with_blanks)
    assert len(tickets) == 2
    assert all(t.ticket_number for t in tickets)


def test_raises_on_missing_column(xlsx_no_ticket_col):
    with pytest.raises(ValueError, match="Ticket number"):
        read_xlsx(xlsx_no_ticket_col)


def test_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        read_xlsx("does_not_exist.xlsx")


def test_accepts_string_path(sample_xlsx):
    assert len(read_xlsx(str(sample_xlsx))) > 0
