
#tests for not yet valid certificate analysis 
import unittest
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from tls.tls_vulnerability_analyzer import Analyze_Certificate


class NotYetValidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test.local")])
        cls.start = datetime(2030, 1, 1, tzinfo=timezone.utc)
        cls.end = datetime(2031, 1, 1, tzinfo=timezone.utc)
        cls.certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(cls.start)
            .not_valid_after(cls.end)
            .sign(key, hashes.SHA256())
        )

    def test_before_start_date(self):
        result = Analyze_Certificate(
            self.certificate, at_time=datetime(2029, 12, 31, tzinfo=timezone.utc)
        )
        check = result["not_yet_valid_analysis"]
        self.assertEqual(result["status"], "NOT_YET_VALID")
        self.assertEqual(check["check"], "tls_certificate_not_yet_valid")
        self.assertEqual(check["status"], "NOT_YET_VALID")
        self.assertTrue(check["is_not_yet_valid"])
        self.assertEqual(check["valid_from_utc"], self.start.isoformat())

    def test_at_start_date(self):
        result = Analyze_Certificate(self.certificate, at_time=self.start)
        check = result["not_yet_valid_analysis"]
        self.assertEqual(check["status"], "START_DATE_PASSED")
        self.assertFalse(check["is_not_yet_valid"])

    def test_after_start_date(self):
        result = Analyze_Certificate(
            self.certificate, at_time=datetime(2030, 6, 1, tzinfo=timezone.utc)
        )
        check = result["not_yet_valid_analysis"]
        self.assertEqual(check["status"], "START_DATE_PASSED")
        self.assertFalse(check["is_not_yet_valid"])
        self.assertEqual(result["status"], "NOT_EXPIRED")

    def test_expired_certificate_does_not_count_as_not_yet_valid(self):
        result = Analyze_Certificate(
            self.certificate, at_time=datetime(2032, 1, 1, tzinfo=timezone.utc)
        )
        self.assertEqual(result["status"], "EXPIRED")
        self.assertFalse(result["not_yet_valid_analysis"]["is_not_yet_valid"])


if __name__ == "__main__":
    unittest.main()
