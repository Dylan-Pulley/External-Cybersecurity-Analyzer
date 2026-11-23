from tls.tls_certificate_retriever import GetCertificate

tests = [
    ("Empty URL", ""),
    ("Invalid protocol", "ftp://example.com"),
    ("Invalid port", "https://example.com:99999"),
    ("Invalid port text", "https://example.com:abc"),
    ("DNS failure", "https://nonexistent.invalid"),
    ("Connection refused", "https://127.0.0.1:1"),
    ("TLS handshake failure", "https://example.com:80"),
    ("HTTP fallback", "http://127.0.0.1"),
    ("Successful connection", "https://example.com"),
]

for name, URL in tests:
    print(f"\nTesting: {name}")
    print(f"URL: {URL}")

    try:
        result = GetCertificate(URL)

        if result is None:
            print("Result: No certificate returned")
        else:
            print("Result: Certificate retrieved")

    except ValueError as error:
        print(f"Caught ValueError: {error}")

    except RuntimeError as error:
        print(f"Caught RuntimeError: {error}")

    except Exception as error:
        print(f"Unexpected error: {type(error).__name__}: {error}")