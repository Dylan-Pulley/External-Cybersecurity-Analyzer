import unittest
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.x509.oid import NameOID

from tls.tls_vulnerability_analyzer import Analyze_Certificate


class SelfSignedTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 21, tzinfo=timezone.utc)

    def make_certificate(self, subject, issuer, subject_key, signing_key, algorithm=None):
        if algorithm is None and not isinstance(signing_key, ed25519.Ed25519PrivateKey):
            algorithm = hashes.SHA256()
        return (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)]))
            .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer)]))
            .public_key(subject_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime(2025, 1, 1, tzinfo=timezone.utc))
            .not_valid_after(datetime(2030, 1, 1, tzinfo=timezone.utc))
            .sign(signing_key, algorithm)
        )

    def test_self_signed_rsa_certificate(self):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        certificate = self.make_certificate("local.test", "local.test", key, key)

        result = Analyze_Certificate(certificate, at_time=self.now)
        check = result["self_signed_analysis"]
        self.assertEqual(check["check"], "tls_certificate_self_signed")
        self.assertEqual(check["status"], "SELF_SIGNED")
        self.assertTrue(check["is_self_signed"])
        self.assertEqual(check["subject"], "CN=local.test")
        self.assertEqual(check["issuer"], "CN=local.test")
        self.assertEqual(result["status"], "NOT_EXPIRED")
        self.assertFalse(result["not_yet_valid_analysis"]["is_not_yet_valid"])

    def test_ca_signed_certificate(self):
        ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        certificate = self.make_certificate("server.test", "Example CA", server_key, ca_key)

        check = Analyze_Certificate(certificate, at_time=self.now)["self_signed_analysis"]
        self.assertEqual(check["status"], "NOT_SELF_SIGNED")
        self.assertFalse(check["is_self_signed"])

    def test_same_names_but_signature_from_different_key(self):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        another_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        certificate = self.make_certificate("local.test", "local.test", key, another_key)

        check = Analyze_Certificate(certificate, at_time=self.now)["self_signed_analysis"]
        self.assertEqual(check["status"], "NOT_SELF_SIGNED")
        self.assertFalse(check["is_self_signed"])

    def test_self_signed_elliptic_curve_certificate(self):
        key = ec.generate_private_key(ec.SECP256R1())
        certificate = self.make_certificate("ec.test", "ec.test", key, key)

        check = Analyze_Certificate(certificate, at_time=self.now)["self_signed_analysis"]
        self.assertTrue(check["is_self_signed"])

    def test_self_signed_ed25519_certificate(self):
        key = ed25519.Ed25519PrivateKey.generate()
        certificate = self.make_certificate("ed.test", "ed.test", key, key)

        check = Analyze_Certificate(certificate, at_time=self.now)["self_signed_analysis"]
        self.assertTrue(check["is_self_signed"])


if __name__ == "__main__":
    unittest.main()
