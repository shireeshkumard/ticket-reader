from dataclasses import dataclass


@dataclass
class Ticket:
    """A single support ticket record."""

    ticket_number: str
    description: str
    status: str
    owner: str
    issue_type: str

    def __str__(self) -> str:
        return f"[{self.issue_type}] {self.ticket_number}: {self.description}"
