import csv
import sys

def read_tickets(filepath="Tickets.csv"):
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers:
                print("Error: CSV file is empty or has no headers.")
                sys.exit(1)

            ticket_col = next(
                (h for h in headers if "ticket" in h.lower() and "number" in h.lower()),
                next((h for h in headers if "ticket" in h.lower()), None)
            )

            if not ticket_col:
                print(f"Could not find a ticket number column. Available columns: {headers}")
                sys.exit(1)

            print(f"Ticket Numbers (column: '{ticket_col}'):")
            for row in reader:
                print(row[ticket_col])

    except FileNotFoundError:
        print(f"Error: '{filepath}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "Tickets.csv"
    read_tickets(filepath)
