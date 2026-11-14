from urllib.parse import urlsplit#break into url components like scheme, hostname, and port

from sslyze import (
    ScanCommand, #specifies type of security sslyze should perform
    ScanCommandAttemptStatusEnum,#indicates individual scan command completed
    Scanner,#manages & executes scan requests
    ServerNetworkLocation,#Identifies server and port to contact
    ServerScanRequest,#Packages target and scan commands into a request
    ServerScanStatusEnum#enumurates through server scans completed 
)


def GetCertificate(URL):
    if "://" not in URL:#fix url
        URL = "https://" + URL

    target = urlsplit(URL)#seperate url

    if target.scheme != "https" or not target.hostname:
        raise ValueError("A valid HTTPS URL is required")

    hostname = target.hostname
    port = target.port or 443#443 set to default target

    request = ServerScanRequest(
        server_location=ServerNetworkLocation(
            hostname=hostname,
            port=port
        ),
        scan_commands={ScanCommand.CERTIFICATE_INFO}
    )

    scanner = Scanner()#create sslyze scanner object
    scanner.queue_scans([request])#accept multiple requests

    result = next(scanner.get_results())#grab results as they arrive, built for scalability

    if result.scan_status != ServerScanStatusEnum.COMPLETED:#error check for scan complete
        raise RuntimeError("TLS connection failed")

    #scan_result = requested scan commands
    certificate_scan = result.scan_result.certificate_info

    #check for scan status = complete
    if certificate_scan.status != ScanCommandAttemptStatusEnum.COMPLETED:
        raise RuntimeError("Certificate retrieval failed")

    for deployment in certificate_scan.result.certificate_deployments:#scan for multiple certs
        if deployment.received_certificate_chain:
            certificate = deployment.received_certificate_chain[0]
            return certificate

    raise RuntimeError("No TLS certificate found")


if __name__ == "__main__":
    certificate = GetCertificate("https://example.org")

    #later add here return subject, issuer, ssn, validity, and expiration date
    print("Subject:", certificate.subject)
    print("Issuer:", certificate.issuer)
    print("Serial Number:", certificate.serial_number)
    print("Valid From:", certificate.not_valid_before_utc)
    print("Valid Until:", certificate.not_valid_after_utc)
