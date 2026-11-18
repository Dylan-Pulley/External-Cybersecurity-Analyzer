import unittest
from unittest.mock import patch

from port import port_getter


class GetOpenPortsTests(unittest.TestCase):
    @patch.object(port_getter.nmap, "PortScanner")
    def test_missing_host_raises_error(self, mock_port_scanner):
        ip = "127.0.0.1"
        scanner = mock_port_scanner.return_value
        scanner.all_hosts.return_value = []

        with self.assertRaisesRegex(RuntimeError, "Nmap returned no host result"):
            port_getter.Get_Open_Ports(ip)

    @patch.object(port_getter.nmap, "PortScanner")
    def test_host_with_only_closed_ports_returns_empty_list(self, mock_port_scanner):
        ip = "127.0.0.1"
        scanner = mock_port_scanner.return_value
        scanner.all_hosts.return_value = [ip]

        host = scanner.__getitem__.return_value
        host.state.return_value = "up"
        host.all_tcp.return_value = [443]
        host.__getitem__.return_value = {443: {"state": "closed"}}

        self.assertEqual(port_getter.Get_Open_Ports(ip), [])

    @patch.object(port_getter.nmap, "PortScanner")
    def test_scan_timeout_raises_clear_error(self, mock_port_scanner):
        scanner = mock_port_scanner.return_value
        scanner.scan.side_effect = port_getter.nmap.PortScannerTimeout(
            "Timeout from nmap process"
        )

        with self.assertRaisesRegex(RuntimeError, "timed out after 300 seconds"):
            port_getter.Get_Open_Ports("127.0.0.1")

    @patch.object(port_getter.nmap, "PortScanner")
    def test_nmap_startup_failure_raises_clear_error(self, mock_port_scanner):
        mock_port_scanner.side_effect = port_getter.nmap.PortScannerError(
            "nmap program was not found in path"
        )

        with self.assertRaisesRegex(RuntimeError, "Could not start Nmap"):
            port_getter.Get_Open_Ports("127.0.0.1")

    @patch.object(port_getter.nmap, "PortScanner")
    def test_scan_failure_raises_clear_error(self, mock_port_scanner):
        scanner = mock_port_scanner.return_value
        scanner.scan.side_effect = port_getter.nmap.PortScannerError(
            "Nmap failed during the scan"
        )

        with self.assertRaisesRegex(RuntimeError, "Nmap could not complete the scan"):
            port_getter.Get_Open_Ports("127.0.0.1")

    @patch.object(port_getter.nmap, "PortScanner")
    def test_host_marked_down_raises_error(self, mock_port_scanner):
        ip = "127.0.0.1"
        scanner = mock_port_scanner.return_value
        scanner.all_hosts.return_value = [ip]

        host = scanner.__getitem__.return_value
        host.state.return_value = "down"

        with self.assertRaisesRegex(RuntimeError, "Open ports could not be determined"):
            port_getter.Get_Open_Ports(ip)

        host.all_tcp.assert_not_called()