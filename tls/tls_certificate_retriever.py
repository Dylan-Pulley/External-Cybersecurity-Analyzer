import ipaddress
import socket
import ssl
from datetime import datetime, timezone
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

    try:
        target = urlsplit(URL)

        if target.scheme not in ("http", "https") or not target.hostname or target.username or target.password:
            raise ValueError("Enter a valid HTTP/HTTPS URL, hostname, or IP address")

        hostname = target.hostname
        requested_port = target.port

    except ValueError as error:
        raise ValueError(f"Invalid URL: {error}") from error

    # HTTP has no certificate, so check HTTPS on port 443.
    port = 443 if target.scheme == "http" else requested_port or 443

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((hostname, port), timeout=10) as connection:
            with context.wrap_socket(connection, server_hostname=hostname) as tls_connection:
                certificate_data = tls_connection.getpeercert(binary_form=True)

    except socket.timeout as error:
        message = f"Connection to {hostname}:{port} timed out"
        if target.scheme == "http":
            print(message)
            return None
        raise RuntimeError(message) from error

    except socket.gaierror as error:
        message = f"Could not resolve hostname: {hostname}"
        if target.scheme == "http":
            print(message)
            return None
        raise RuntimeError(message) from error

    except ConnectionRefusedError as error:
        message = f"Connection refused on {hostname}:{port}"
        if target.scheme == "http":
            print(message)
            return None
        raise RuntimeError(message) from error

    except ssl.SSLError as error:
        message = f"TLS handshake failed on {hostname}:{port}: {error}"
        if target.scheme == "http":
            print(message)
            return None
        raise RuntimeError(message) from error

    except OSError as error:
        message = f"Network error on {hostname}:{port}: {error}"
        if target.scheme == "http":
            print(message)
            return None
        raise RuntimeError(message) from error

    if not certificate_data:
        if target.scheme == "http":
            print(f"HTTPS did not provide a certificate on {hostname}:{port}")
            return None
        raise RuntimeError("No TLS certificate found")

    try:
        certificate = x509.load_der_x509_certificate(certificate_data)
    except ValueError as error:
        raise RuntimeError("Certificate data is invalid") from error

    print("Certificate retrieved successfully")
    print("Subject:", certificate.subject.rfc4514_string())
    print("Issuer:", certificate.issuer.rfc4514_string())
    print("Serial Number:", certificate.serial_number)
    print("Valid From:", certificate.not_valid_before_utc)
    print("Valid Until:", certificate.not_valid_after_utc)

    current_time = datetime.now(timezone.utc)

    if current_time > certificate.not_valid_after_utc:
        print("Warning: Certificate has expired")

    elif current_time < certificate.not_valid_before_utc:
        print("Warning: Certificate is not yet valid")

    return certificate