
import ipaddress  #converts localhost IP into a certificate-compatible IP object
import ssl  #adds HTTPS encryption to the local web server
import tempfile  #creates a temporary folder for the certificate files
from datetime import datetime, timedelta, timezone  #sets the certificate dates
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  #basic Python web server
from pathlib import Path  #helps make certificate file paths

from cryptography import x509  #creates the test TLS certificate
from cryptography.hazmat.primitives import hashes, serialization  #signs and saves certificate files
from cryptography.hazmat.primitives.asymmetric import rsa  #generates the private key
from cryptography.x509.oid import NameOID  #sets the name on the certificate


def Generate_Expired_Certificate(FOLDER):
    private_key = rsa.generate_private_key(  #make a private key for the localhost server
        public_exponent=65537,
        key_size=2048
    )

    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost")  #certificate belongs to localhost
    ])

    today = datetime.now(timezone.utc)

    certificate = (
        x509.CertificateBuilder()  #build a self-signed test certificate
        .subject_name(name)
        .issuer_name(name)  #issuer and subject match because it is self-signed
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(today - timedelta(days=60))  #certificate started being valid 60 days ago
        .not_valid_after(today - timedelta(days=1))  #certificate expired yesterday on purpose
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1"))  #allow either localhost or its IP
            ]),
            critical=False
        )
        .sign(private_key, hashes.SHA256())  #sign with the private key
    )

    certificate_file = Path(FOLDER) / "expired_certificate.pem"
    key_file = Path(FOLDER) / "private_key.pem"

    certificate_file.write_bytes(
        certificate.public_bytes(serialization.Encoding.PEM)  #save the certificate to a PEM file
    )

    key_file.write_bytes(private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ))  #save the private key for the local server

    return certificate_file, key_file  #return both paths so HTTPS can use them


class Test_Website(BaseHTTPRequestHandler):
    def do_GET(self):  #sends a simple HTML page when someone visits the site
        page = b"<h1>Local TLS Test Website</h1><p>This certificate is intentionally expired.</p>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)  #send the page to the browser or test client


def Create_Server(CERTIFICATE_FILE, KEY_FILE, PORT=8443):
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Test_Website)  #listen on this computer only
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  #create the HTTPS server configuration

    try:
        context.load_cert_chain(str(CERTIFICATE_FILE), str(KEY_FILE))  #load the expired certificate and key
        server.socket = context.wrap_socket(
            server.socket,
            server_side=True
        )  #make the web server use HTTPS
    except Exception:
        server.server_close()  #close the port if HTTPS setup fails
        raise

    return server


def main():
    with tempfile.TemporaryDirectory() as folder:  #certificate files are temporary
        certificate_file, key_file = Generate_Expired_Certificate(folder)

        with Create_Server(certificate_file, key_file) as server:
            print("Local HTTPS test website: https://localhost:8443", flush=True)
            print("Certificate expired: YES (1 day ago)", flush=True)
            print("Press Ctrl+C to stop the server.", flush=True)

            try:
                server.serve_forever()  #keep serving until the user stops it
            except KeyboardInterrupt:
                print("\nServer stopped.")


if __name__ == "__main__":
    main()  #start website only when this file is run directly
