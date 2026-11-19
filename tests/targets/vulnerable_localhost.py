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

#Ports
from threading import Thread


class Test_Website(BaseHTTPRequestHandler):
    def do_GET(self):
        page = b"<h1>Local TLS Test Website</h1><p>This certificate is intentionally expired.</p>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

def Open_Port(PORT, CONTEXT, SERVERS):
    if PORT in SERVERS:
        print(f"Port {PORT} is already in use.")
        return

    server = None

    try:
        server = ThreadingHTTPServer(
            ("127.0.0.1", PORT),
            Test_Website
        )
        server.socket = CONTEXT.wrap_socket(server.socket, server_side=True)
    except OSError as error:
        if server is not None:
            server.server_close()
        print(f"Failed to open port {PORT}: {error}")
        return

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    SERVERS[PORT] = (server, thread)
    print(f"Opened https://localhost:{PORT}")

def Close_Port(PORT, SERVERS):
    entry = SERVERS.pop(PORT, None)
    
    if entry is None:
        print(f"Port {PORT} is not currently open.")
        return

    server, thread = entry
    server.shutdown()
    server.server_close()
    thread.join()
    print(f"Closed port {PORT}")


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

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(certificate_file), str(key_file))

        servers = {}

        print("Certificate: expired and self signed")
        print("Commands: open PORT, close PORT, list, quit")

        try:
            Open_Port(8443, context, servers)

            while True:
                parts = input("> ").strip().lower().split()

                if not parts:
                    continue

                command = parts[0]

                if command == "quit" and len(parts) == 1:
                    break
                if command == "list" and len(parts) == 1:
                    if servers:
                        for port in sorted(servers):
                            print(f"https://localhost:{port}")
                    else:
                        print("No ports are currently open.")
                    continue
                if command in ("open", "close") and len(parts) == 2:
                    try:
                        port = int(parts[1])
                    except ValueError:
                        print("Port must be an integer.")
                        continue

                    if not 1 <= port <= 65535:
                        print("Port must be between 1 and 65535.")
                        continue

                    if command == "open":
                        Open_Port(port, context, servers)
                    else:
                        Close_Port(port, servers)
                    continue
                print("Invalid command. Use 'open PORT', 'close PORT', 'list', or 'quit'.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
        finally:
            for port in list(servers.keys()):
                Close_Port(port, servers)


if __name__ == "__main__":
    main()
