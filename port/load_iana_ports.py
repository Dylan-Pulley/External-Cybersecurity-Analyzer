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
                for row in csv.DictReader(stream):
                    number = row["Port Number"].strip()
                    protocol = row["Transport Protocol"].strip().lower()
                    service = row["Service Name"].strip()

                    if number.isdecimal() and protocol and service:
                        key = (int(number), protocol)
                        assignments.setdefault(key, set()).add(service)
    except (URLError, TimeoutError) as exc:
        logging.getLogger(__name__).warning("IANA registry unavailable: %s", exc)
        return {}

    return assignments