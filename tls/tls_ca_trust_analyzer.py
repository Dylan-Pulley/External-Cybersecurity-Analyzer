import ipaddress
import socket
import ssl
from urllib.parse import urlsplit


#openSSL verification codes for missing or untrusted cert authorities
UNTRUSTED_CA_ERRORS = {2, 18, 19, 20, 21, 27, 28}


def Analyze_CA_Trust(URL, *, cafile=None):
    #accept same URL, hostname, and IP inputs as GetCertificate
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
        port = 443 if target.scheme == "http" else target.port or 443
    except ValueError as error:
        raise ValueError(f"Invalid URL: {error}") from error

    #use system CA store unless specific test CA files provided
    context = ssl.create_default_context(cafile=cafile)
    context.check_hostname = False  #checks CA trust not hostname match

    try:
        with socket.create_connection((hostname, port), timeout=10) as connection:
            with context.wrap_socket(connection, server_hostname=hostname):
                return {
                    "check": "tls_certificate_authority_trust",
                    "status": "TRUSTED_CA",
                    "is_ca_trusted": True
                }

    except ssl.SSLCertVerificationError as error:
        #sont mistake expired or invalid cert for untrusted CA
        untrusted = error.verify_code in UNTRUSTED_CA_ERRORS
        return {
            "check": "tls_certificate_authority_trust",
            "status": "UNTRUSTED_CA" if untrusted else "OTHER_CERTIFICATE_ERROR",
            "is_ca_trusted": False if untrusted else None,
            "verify_code": error.verify_code,
            "message": error.verify_message
        }

    except (ssl.SSLError, OSError) as error:
        #failed connection isn't proof that CA is untrusted
        return {
            "check": "tls_certificate_authority_trust",
            "status": "CHECK_FAILED",
            "is_ca_trusted": None,
            "message": str(error)
        }
