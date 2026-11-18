import unittest
from unittest.mock import patch

from port import port_analyzer


class AnalyzePortsTests(unittest.TestCase):
    @patch.object(port_analyzer.iana_ports, "load_iana_ports", return_value=None)
    def test_iana_outage_preserves_open_port(self, mock_load_iana_ports):
        results = port_analyzer.Analyze_Ports([{"port": 443, "service": ""}])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["port"], 443)
        self.assertEqual(results[0]["iana_lookup_status"], "unavailable")
        mock_load_iana_ports.assert_called_once()

    @patch.object(
        port_analyzer.iana_ports,
        "load_iana_ports",
        return_value={(80, "tcp"): {"http"}},
    )
    def test_iana_no_match_uses_empty_service_fallback(self, mock_load_iana_ports):
        results = port_analyzer.Analyze_Ports([{"port": 443, "service": ""}])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["port"], 443)
        self.assertEqual(results[0]["service"], "empty_service")
        self.assertNotIn("iana_lookup_status", results[0])
        mock_load_iana_ports.assert_called_once()


    @patch.object(port_analyzer.iana_ports, "load_iana_ports")
    def test_known_service_skips_iana(self, mock_load_iana_ports):
        results = port_analyzer.Analyze_Ports([{"port": 443, "service": "https"}])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["service"], "https")
        mock_load_iana_ports.assert_not_called()

    @patch.object(
        port_analyzer.iana_ports,
        "load_iana_ports",
        return_value={(443, "tcp"): {"https"}},
    )
    def test_iana_match_sets_service_and_source(self, mock_load_iana_ports):
        results = port_analyzer.Analyze_Ports([{"port": 443, "service": ""}])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["service"], "https")
        self.assertEqual(results[0]["service_source"], "iana")
        mock_load_iana_ports.assert_called_once()

    
    @patch.object(port_analyzer.iana_ports, "load_iana_ports", return_value=None)
    def test_iana_outage_is_attempted_once_for_multiple_ports(
        self, mock_load_iana_ports
    ):
        results = port_analyzer.Analyze_Ports([
            {"port": 443, "service": "https"},
            {"port": 8080, "service": ""},
            {"port": 8443, "service": "unknown"},
        ])

        self.assertEqual(len(results), 3)
        by_port = {result["port"]: result for result in results}
        self.assertEqual(set(by_port), {443, 8080, 8443})

        self.assertEqual(by_port[443]["service"], "https")
        self.assertNotIn("iana_lookup_status", by_port[443])
        self.assertEqual(by_port[8080]["iana_lookup_status"], "unavailable")
        self.assertEqual(by_port[8443]["iana_lookup_status"], "unavailable")
        mock_load_iana_ports.assert_called_once()