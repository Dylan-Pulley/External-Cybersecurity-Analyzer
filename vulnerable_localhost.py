import ipaddress  # lets the certificate use the localhost IP
import ssl  # adds HTTPS to the server
import tempfile  # holds the temporary certificate files
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class Test_Website(BaseHTTPRequestHandler):
    def do_GET(self):
        page = b"<h1>Local TLS Test Website</h1><p>This certificate is intentionally expired.</p>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)


def main():
    with tempfile.TemporaryDirectory() as folder:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost")
        ])

        today = datetime.now(timezone.utc)

        certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)  # self-signed certificate
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(today - timedelta(days=60))
            .not_valid_after(today - timedelta(days=1))  # expired yesterday
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.ip_address("127.0.0.1"))
                ]),
                critical=False
            )
            .sign(private_key, hashes.SHA256())
        )

        certificate_file = Path(folder) / "expired_certificate.pem"
        key_file = Path(folder) / "private_key.pem"

        certificate_file.write_bytes(
            certificate.public_bytes(serialization.Encoding.PEM)
        )
        key_file.write_bytes(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ))

        server = ThreadingHTTPServer(("127.0.0.1", 8443), Test_Website)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        try:
            context.load_cert_chain(str(certificate_file), str(key_file))
            server.socket = context.wrap_socket(server.socket, server_side=True)
        except Exception:
            server.server_close()
            raise

        info = {
            "url": "https://localhost:8443",
            "certificate_status": "EXPIRED",
            "valid_from_utc": certificate.not_valid_before_utc.isoformat(),
            "expires_at_utc": certificate.not_valid_after_utc.isoformat(),
            "self_signed": True
        }

        print("Local HTTPS test website:", info["url"], flush=True)
        print("Certificate Status:", info["certificate_status"], flush=True)
        print("Valid From (UTC):", info["valid_from_utc"], flush=True)
        print("Expires (UTC):", info["expires_at_utc"], flush=True)
        print("Self-Signed:", info["self_signed"], flush=True)
        print("Press Ctrl+C to stop the server.", flush=True)

        with server:
            try:
                server.serve_forever()  # stays online for the TLS scanner
            except KeyboardInterrupt:
                print("\nServer stopped.")

        return info  # returned after the server stops


if __name__ == "__main__":
    main()
