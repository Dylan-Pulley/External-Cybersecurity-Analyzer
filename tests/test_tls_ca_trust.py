
#! Tests the CA-trust check using temporary local HTTPS servers.
import ipaddress
import socket
import ssl
import tempfile
import threading
import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from tls.tls_ca_trust_analyzer import Analyze_CA_Trust


def make_certificates(*, self_signed=False, expired=False):
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Temporary Test CA")])
    ca_certificate = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=10))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=False, key_cert_sign=True,
            crl_sign=True, encipher_only=False, decipher_only=False
        ), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    server_key = ca_key if self_signed else rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_name = ca_name if self_signed else x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost")
    ])
    server_certificate = (
        x509.CertificateBuilder()
        .subject_name(server_name)
        .issuer_name(ca_name)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=30))
        .not_valid_after(now - timedelta(days=1) if expired else now + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=False, key_encipherment=True,
            data_encipherment=False, key_agreement=False, key_cert_sign=False,
            crl_sign=False, encipher_only=False, decipher_only=False
        ), critical=True)
        .add_extension(x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.ip_address("127.0.0.1"))
        ]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    return ca_certificate, server_certificate, server_key


@contextmanager
def local_https_server(certificate, key):
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        certificate_path = folder / "server.pem"
        key_path = folder / "server.key"
        certificate_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        key_path.write_bytes(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(certificate_path), str(key_path))

        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            listener.settimeout(5)
            port = listener.getsockname()[1]

            def serve_once():
                try:
                    connection, _ = listener.accept()
                    with connection:
                        with context.wrap_socket(connection, server_side=True) as secure:
                            secure.recv(1)
                except (OSError, ssl.SSLError):
                    pass  #! The client closes the connection after verifying the certificate.

            thread = threading.Thread(target=serve_once, daemon=True)
            thread.start()
            try:
                yield f"https://127.0.0.1:{port}", folder
            finally:
                thread.join(timeout=6)


class CATrustTests(unittest.TestCase):
    def test_trusted_ca(self):
        ca, certificate, key = make_certificates()
        with local_https_server(certificate, key) as (url, folder):
            ca_path = folder / "trusted_ca.pem"
            ca_path.write_bytes(ca.public_bytes(serialization.Encoding.PEM))
            result = Analyze_CA_Trust(url, cafile=str(ca_path))
        self.assertEqual(result["status"], "TRUSTED_CA")
        self.assertTrue(result["is_ca_trusted"])

    def test_untrusted_ca(self):
        _, certificate, key = make_certificates()
        with local_https_server(certificate, key) as (url, _):
            result = Analyze_CA_Trust(url)
        self.assertEqual(result["status"], "UNTRUSTED_CA")
        self.assertFalse(result["is_ca_trusted"])
        self.assertIn("verify_code", result)

    def test_untrusted_self_signed_certificate(self):
        _, certificate, key = make_certificates(self_signed=True)
        with local_https_server(certificate, key) as (url, _):
            result = Analyze_CA_Trust(url)
        self.assertEqual(result["status"], "UNTRUSTED_CA")
        self.assertFalse(result["is_ca_trusted"])

    def test_expired_certificate_is_a_different_error(self):
        ca, certificate, key = make_certificates(expired=True)
        with local_https_server(certificate, key) as (url, folder):
            ca_path = folder / "trusted_ca.pem"
            ca_path.write_bytes(ca.public_bytes(serialization.Encoding.PEM))
            result = Analyze_CA_Trust(url, cafile=str(ca_path))
        self.assertEqual(result["status"], "OTHER_CERTIFICATE_ERROR")
        self.assertIsNone(result["is_ca_trusted"])

    def test_connection_failure_is_not_untrusted_ca(self):
        with patch("tls.tls_ca_trust_analyzer.socket.create_connection", side_effect=ConnectionRefusedError("refused")):
            result = Analyze_CA_Trust("https://localhost:9443")
        self.assertEqual(result["status"], "CHECK_FAILED")
        self.assertIsNone(result["is_ca_trusted"])

    def test_bad_url_is_rejected(self):
        with self.assertRaises(ValueError):
            Analyze_CA_Trust("ftp://invalid.test")


if __name__ == "__main__":
    unittest.main()
