import io
import unittest
from unittest.mock import patch

from port.load_iana_ports import load_iana_ports


class LoadIanaPortsTests(unittest.TestCase):
    @patch("port.load_iana_ports.urlopen")
    def test_missing_required_csv_column_returns_none(self, mock_urlopen):
        mock_urlopen.return_value = io.BytesIO(
            b"Port Number,Service Name\n443,https\n"
        )

        with self.assertLogs("port.load_iana_ports", level="WARNING") as logs:
            self.assertIsNone(load_iana_ports())

        self.assertIn("missing required columns", logs.output[0])

    @patch("port.load_iana_ports.urlopen")
    def test_valid_csv_loads_every_row(self, mock_urlopen):
        mock_urlopen.return_value = io.BytesIO(
            b"Port Number,Transport Protocol,Service Name\n"
            b"80,tcp,http\n"
            b"443,tcp,https\n"
        )

        self.assertEqual(
            load_iana_ports(),
            {(80, "tcp"): {"http"}, (443, "tcp"): {"https"}},
        )

    @patch("port.load_iana_ports.urlopen")
    def test_connection_reset_while_reading_returns_none(self, mock_urlopen):
        class ResettingResponse(io.BytesIO):
            def read1(self, size=-1):
                raise ConnectionResetError("Connection reset while reading")

        mock_urlopen.return_value = ResettingResponse()

        with self.assertLogs("port.load_iana_ports", level="WARNING") as logs:
            self.assertIsNone(load_iana_ports())

        self.assertIn("Connection reset while reading", logs.output[0])