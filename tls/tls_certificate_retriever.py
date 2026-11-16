from urllib.parse import urlsplit  # breaks the URL into parts

from sslyze import (
    ScanCommand,
    ScanCommandAttemptStatusEnum,
    Scanner,
    ServerNetworkLocation,
    ServerScanRequest,
    ServerScanStatusEnum
)


def GetCertificate(URL):
    if "://" not in URL:
        URL = "https://" + URL

    target = urlsplit(URL)

    if target.scheme != "https" or not target.hostname:
        raise ValueError("A valid HTTPS URL is required")

    hostname = target.hostname
    port = target.port or 443

    request = ServerScanRequest(
        server_location=ServerNetworkLocation(
            hostname=hostname,
            port=port
        ),
        scan_commands={ScanCommand.CERTIFICATE_INFO}
    )

    scanner = Scanner()
    scanner.queue_scans([request])
    result = next(scanner.get_results())

    if result.scan_status != ServerScanStatusEnum.COMPLETED:
        raise RuntimeError("TLS connection failed")

    certificate_scan = result.scan_result.certificate_info

    if certificate_scan.status != ScanCommandAttemptStatusEnum.COMPLETED:
        raise RuntimeError("Certificate retrieval failed")

    for deployment in certificate_scan.result.certificate_deployments:
        if deployment.received_certificate_chain:
            certificate = deployment.received_certificate_chain[0]

            print("Certificate retrieved successfully")
            print("Subject:", certificate.subject.rfc4514_string())
            print("Issuer:", certificate.issuer.rfc4514_string())
            print("Serial Number:", certificate.serial_number)
            print("Valid From:", certificate.not_valid_before_utc)
            print("Valid Until:", certificate.not_valid_after_utc)

            return certificate  # gives the certificate to the analyzer

    raise RuntimeError("No TLS certificate found")
