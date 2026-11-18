import csv
import io
import logging
from urllib.error import URLError
from urllib.request import urlopen

IANA_PORTS_URL = (
    "https://www.iana.org/assignments/service-names-port-numbers/"
    "service-names-port-numbers.csv"
)

def load_iana_ports():
    assignments = {}

    try:
        with urlopen(IANA_PORTS_URL, timeout=5) as response:
            with io.TextIOWrapper(response, encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                required_columns = {"Port Number", "Transport Protocol", "Service Name"}

                if not required_columns.issubset(reader.fieldnames or ()):
                    raise csv.Error("IANA registry is missing required columns")

                for row in reader:
                    if any(row[column] is None for column in required_columns):
                        raise csv.Error(f"IANA registry has an incomplete row at line {reader.line_num}")

                    number = row["Port Number"].strip()
                    protocol = row["Transport Protocol"].strip().lower()
                    service = row["Service Name"].strip()

                    if number.isdecimal() and protocol and service:
                        key = (int(number), protocol)
                        assignments.setdefault(key, set()).add(service)

    except (URLError, TimeoutError, ConnectionResetError, UnicodeDecodeError, csv.Error) as exc:
        logging.getLogger(__name__).warning("IANA registry unavailable: %s", exc)
        return None

    return assignments