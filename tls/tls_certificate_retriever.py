
import ipaddress
import socket
import ssl
from urllib.parse import urlsplit

from cryptography import x509


def GetCertificate(URL):
    if not isinstance(URL, str) or not URL.strip():
        raise ValueError("Enter an HTTP/HTTPS URL, hostname, or IP address")

    URL = URL.strip()

    if "://" not in URL:
        try:
            if ipaddress.ip_address(URL).version == 6:
                URL = f"[{URL}]"
        except ValueError:
            pass
        URL = "https://" + URL

    target = urlsplit(URL)

    if target.scheme not in ("http", "https") or not target.hostname or target.username or target.password:
        raise ValueError("Enter an HTTP/HTTPS URL, hostname, or IP address")

    hostname = target.hostname
    # HTTP has no certificate, so check whether the same host offers HTTPS on port 443.
    requested_port = target.port
    port = 443 if target.scheme == "http" else requested_port or 443

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((hostname, port), timeout=10) as connection:
            with context.wrap_socket(connection, server_hostname=hostname) as tls_connection:
                certificate_data = tls_connection.getpeercert(binary_form=True)
    except (OSError, ssl.SSLError) as error:
        if target.scheme == "http":
            print(f"HTTPS unavailable on {hostname}:443: {error}")
            return None
        raise RuntimeError(f"TLS connection to {hostname}:{port} failed: {error}") from error

    if not certificate_data:
        if target.scheme == "http":
            print(f"HTTPS did not provide a certificate on {hostname}:443")
            return None
        raise RuntimeError("No TLS certificate found")

    certificate = x509.load_der_x509_certificate(certificate_data)

    print("Certificate retrieved successfully")
    print("Subject:", certificate.subject.rfc4514_string())
    print("Issuer:", certificate.issuer.rfc4514_string())
    print("Serial Number:", certificate.serial_number)
    print("Valid From:", certificate.not_valid_before_utc)
    print("Valid Until:", certificate.not_valid_after_utc)

    return certificate
