"""Verify the deployed image can use Nmap, without scanning any hosts."""
import shutil
import unittest
from unittest.mock import patch

import nmap
from fastapi.testclient import TestClient

from app import app


class RuntimeTests(unittest.TestCase):
    def test_nmap_executable_is_available(self):
        self.assertIsNotNone(shutil.which("nmap"))
        self.assertTrue(nmap.PortScanner().nmap_version())

    def test_homepage_and_scan_response(self):
        results = {"ports": [], "tls": {"status": "NOT_EXPIRED"}}
        with TestClient(app) as client:
            self.assertEqual(client.get("/").status_code, 200)
            with patch("app.main.main", return_value=results) as scan:
                response = client.post("/api/scan", json={
                    "website": "https://example.com", "has_permission": True,
                })
                scan.assert_called_once_with("https://example.com")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                "website": "https://example.com", "results": results,
            })

    def test_scan_returns_port_error_alongside_tls_result(self):
        website = "https://example.com"
        port_error = "Nmap could not complete the scan."
        tls_result = {"status": "NOT_EXPIRED"}

        with (
            patch("app.main.Get_IP", return_value="192.0.2.1"),
            patch("app.main.Port_Analyzer", side_effect=RuntimeError(port_error)),
            patch("app.main.TLS_Analyzer", return_value=tls_result),
            TestClient(app) as client,
        ):
            response = client.post(
                "/api/scan",
                json={"website": website, "has_permission": True},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "website": website,
            "results": {
                "ports": {"error": port_error},
                "tls": tls_result,
            },
        })


if __name__ == "__main__":
    unittest.main()
