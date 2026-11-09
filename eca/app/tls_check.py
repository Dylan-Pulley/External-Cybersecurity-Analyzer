"""Basic TLS connection metadata; this is not a full vulnerability scan."""
import ipaddress
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlsplit


def normalize_host(url):
    value = url.strip()
    if not value or len(value) > 2048 or any(c.isspace() for c in value):
        raise ValueError("Enter a website such as example.com or https://example.com.")
    try:
        parsed = urlsplit(value if "://" in value else "https://" + value)
        host = parsed.hostname
        if (parsed.scheme != "https" or not host or parsed.username is not None
                or parsed.password is not None or parsed.port not in (None, 443)):
            raise ValueError
        host = host.rstrip(".").encode("idna").decode("ascii")
        if not host or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789.-:" for c in host):
            raise ValueError
    except (ValueError, UnicodeError):
        raise ValueError("Use an HTTPS hostname without credentials or a custom port.") from None
    return host


def resolve_public_address(host):
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    if not addresses:
        raise OSError("No address found for this hostname.")
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global or (ip.version == 6 and ip.ipv4_mapped is not None
                                and not ip.ipv4_mapped.is_global):
            raise ValueError("Use a public website; local and private addresses are not supported.")
    return addresses[0]


def check(url):
    host = normalize_host(url)
    try:
        family, socktype, proto, _, address = resolve_public_address(host)
        # Pin the validated address; retain the hostname for TLS identity checks.
        with socket.socket(family, socktype, proto) as raw:
            raw.settimeout(5)
            raw.connect(address)
            with ssl.create_default_context().wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert()
                expires = datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]), timezone.utc)
                return {
                    "host": host, "ok": True,
                    "protocol": tls.version(), "cipher": tls.cipher()[0],
                    "expires": expires.date().isoformat(),
                    "days_left": (expires - datetime.now(timezone.utc)).days,
                }
    except ssl.SSLCertVerificationError as exc:
        return {"host": host, "ok": False, "problem": exc.verify_message}
    except OSError:
        return {"host": host, "ok": False,
                "problem": "Could not establish a TLS connection. Check the hostname and try again."}
