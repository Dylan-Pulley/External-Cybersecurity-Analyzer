from datetime import datetime, timezone

from tls.tls_certificate_retriever import GetCertificate
from tls.tls_vulnerability_analyzer import Analyze_Certificate


tests = [
    ("Missing certificate", None),
    ("Invalid certificate type", "not a certificate"),
    ("Invalid certificate number", 12345),
]

for name, certificate in tests:
    print(f"\nTesting: {name}")

    try:
        result = Analyze_Certificate(certificate)
        print("Result:", result)

    except (TypeError, ValueError, RuntimeError) as error:
        print(f"Caught {type(error).__name__}: {error}")


print("\nTesting: Missing timezone")

try:
    certificate = GetCertificate("https://example.com")
    result = Analyze_Certificate(
        certificate,
        at_time=datetime(2026, 11, 20)
    )

except (TypeError, ValueError, RuntimeError) as error:
    print(f"Caught {type(error).__name__}: {error}")


print("\nTesting: Expired certificate")

try:
    result = Analyze_Certificate(
        certificate,
        at_time=datetime(2030, 1, 1, tzinfo=timezone.utc)
    )
    print("Result:", result)

except (TypeError, ValueError, RuntimeError) as error:
    print(f"Caught {type(error).__name__}: {error}")